package tn

import (
	"errors"
	"io"
	"net"
	"sync"
	"time"
)

const (
	IAC  = 255 // Interpret As Command
	DONT = 254
	DO   = 253
	WONT = 252
	WILL = 251
	SB   = 250
	SE   = 240
)

type ConnWriter struct {
	c  net.Conn
	mu *sync.Mutex
}

func NewConnWriter(c net.Conn) *ConnWriter { return &ConnWriter{c: c, mu: &sync.Mutex{}} }

func (w *ConnWriter) Write(p []byte) (int, error) {
	w.mu.Lock()
	n, err := w.c.Write(p)
	w.mu.Unlock()
	return n, err
}

// TelnetInputFilter reads bytes from telnet server, filters option negotiation,
// and proactively replies with neutral responses (WONT/DONT). Application bytes
// are passed through to the reader.
// It is safe for concurrent use with TelnetOutputEscaper using the same ConnWriter.

type TelnetInputFilter struct {
	conn   net.Conn
	writer *ConnWriter
	buf    []byte // internal decoded buffer
	state  int
	opt    byte
}

const (
	stData = iota
	stIAC
	stIACVerb
	stSB
	stSBData
	stSBDataIAC
)

func NewInputFilter(c net.Conn, w *ConnWriter) *TelnetInputFilter {
	return &TelnetInputFilter{conn: c, writer: w, buf: make([]byte, 0, 8192), state: stData}
}

func (t *TelnetInputFilter) Read(p []byte) (int, error) {
	// If we already have decoded bytes buffered, serve them first.
	if len(t.buf) > 0 {
		n := copy(p, t.buf)
		t.buf = t.buf[n:]
		return n, nil
	}
	// Otherwise, fill from conn and decode.
	tmp := make([]byte, 4096)
	nr, err := t.conn.Read(tmp)
	if err != nil {
		return 0, err
	}
	data := tmp[:nr]
	decoded := t.decode(data)
	if len(decoded) == 0 {
		// No app data produced yet; try again quickly (non-blocking semantics)
		return 0, nil
	}
	n := copy(p, decoded)
	if n < len(decoded) {
		t.buf = append(t.buf, decoded[n:]...)
	}
	return n, nil
}

func (t *TelnetInputFilter) decode(in []byte) []byte {
	out := make([]byte, 0, len(in))
	writeReply := func(b ...byte) {
		// Best effort; ignore errors here.
		_, _ = t.writer.Write(b)
	}
	for i := 0; i < len(in); i++ {
		b := in[i]
		switch t.state {
		case stData:
			if b == IAC {
				t.state = stIAC
				continue
			}
			out = append(out, b)
		case stIAC:
			if b == IAC {
				// Escaped 255
				out = append(out, IAC)
				t.state = stData
				continue
			}
			if b == SB {
				t.state = stSB
				continue
			}
			// Command verb expected (WILL/WONT/DO/DONT)
			switch b {
			case WILL, WONT, DO, DONT:
				t.state = stIACVerb
				t.opt = 0
				t.opt = 0 // reset
				// store verb in opt's hi bit? We'll just track via state; next byte is option
				// abuse opt to remember verb by negative value? Simpler: use separate var
				// embed verb into state via storing as negative not needed; use a small hack
				// We'll store verb in opt (upper nibble) and option in lower after read
				// Instead, keep a shadow variable
				// To keep simple we will reuse opt for verb using 0xF0 mask
				t.opt = b
			default:
				// Other commands (e.g., SE, NOP) -> ignore
				t.state = stData
			}
		case stIACVerb:
			// b is the option code
			verb := t.opt
			opt := b
			switch verb {
			case DO:
				writeReply([]byte{IAC, WONT, opt}...)
			case WILL:
				writeReply([]byte{IAC, DONT, opt}...)
			case DONT, WONT:
				// no-op
			}
			t.state = stData
		case stSB:
			// subnegotiation, read until IAC SE
			if b == IAC {
				t.state = stSBDataIAC
				continue
			}
			// ignore data
		case stSBDataIAC:
			if b == SE {
				// end subnegotiation
				t.state = stData
			} else if b == IAC {
				// Escaped IAC within SB data
				// stay in SB data
				t.state = stSB
			} else {
				// Unexpected, remain in SB mode
				t.state = stSB
			}
		}
	}
	return out
}

// TelnetOutputEscaper writes to telnet server, escaping IAC (255) by doubling it.

type TelnetOutputEscaper struct {
	writer *ConnWriter
}

func NewOutputEscaper(w *ConnWriter) *TelnetOutputEscaper { return &TelnetOutputEscaper{writer: w} }

func (t *TelnetOutputEscaper) Write(p []byte) (int, error) {
	// Expand buffer if contains IAC
	needs := 0
	for _, b := range p {
		if b == IAC { needs++ }
	}
	if needs == 0 {
		return t.writer.Write(p)
	}
	buf := make([]byte, 0, len(p)+needs)
	for _, b := range p {
		buf = append(buf, b)
		if b == IAC { buf = append(buf, IAC) }
	}
	n, err := t.writer.Write(buf)
	if err != nil { return 0, err }
	// Map written bytes back to original count best-effort
	// If partial writes occurred (unlikely with TCP), return proportion.
	if n >= len(buf) {
		return len(p), nil
	}
	// Fallback conservative accounting
	return 0, io.ErrShortWrite
}

func Dial(target string, timeout time.Duration) (net.Conn, error) {
	if timeout <= 0 { timeout = 5 * time.Second }
	c, err := net.DialTimeout("tcp", target, timeout)
	if err != nil { return nil, err }
	return c, nil
}

var ErrClosed = errors.New("telnet closed")
