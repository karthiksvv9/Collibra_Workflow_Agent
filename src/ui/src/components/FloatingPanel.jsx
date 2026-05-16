import React, { useRef, useState } from 'react';

export default function FloatingPanel({ title, children, defaultPosition = { x: 18, y: 78 }, defaultSize = { w: 380, h: 360 }, corner = 'left' }) {
  const [minimized, setMinimized] = useState(false);
  const [pos, setPos] = useState(defaultPosition);
  const [size, setSize] = useState(defaultSize);
  const dragging = useRef(null);

  function startDrag(e) {
    dragging.current = { x: e.clientX, y: e.clientY, px: pos.x, py: pos.y };
    window.addEventListener('mousemove', onDrag);
    window.addEventListener('mouseup', stopDrag);
  }
  function onDrag(e) {
    if (!dragging.current) return;
    const nx = dragging.current.px + e.clientX - dragging.current.x;
    const ny = dragging.current.py + e.clientY - dragging.current.y;
    setPos({ x: Math.max(0, Math.min(window.innerWidth - 80, nx)), y: Math.max(54, Math.min(window.innerHeight - 46, ny)) });
  }
  function stopDrag() {
    dragging.current = null;
    window.removeEventListener('mousemove', onDrag);
    window.removeEventListener('mouseup', stopDrag);
  }

  if (minimized) {
    return (
      <button className={`min-pill ${corner}`} onClick={() => setMinimized(false)}>{title}</button>
    );
  }

  return (
    <section className="floating-panel" style={{ left: pos.x, top: pos.y, width: size.w, height: size.h }}>
      <div className="floating-title" onMouseDown={startDrag}>
        <strong>{title}</strong>
        <button onClick={() => setMinimized(true)}>Minimize</button>
      </div>
      <div className="floating-content">{children}</div>
      <div className="resize-handle" onMouseDown={(e) => {
        const start = { x: e.clientX, y: e.clientY, w: size.w, h: size.h };
        function onResize(ev) {
          setSize({ w: Math.max(280, start.w + ev.clientX - start.x), h: Math.max(180, start.h + ev.clientY - start.y) });
        }
        function stopResize() {
          window.removeEventListener('mousemove', onResize);
          window.removeEventListener('mouseup', stopResize);
        }
        window.addEventListener('mousemove', onResize);
        window.addEventListener('mouseup', stopResize);
      }} />
    </section>
  );
}
