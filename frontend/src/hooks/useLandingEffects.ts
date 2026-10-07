import { useEffect, type RefObject } from 'react';

const CODE_SRC = `from aryacrypt import AryaCrypt

crypto = AryaCrypt()

blob = crypto.encrypt(
    b"hello aryacrypt",
    "password1"
)

plain = crypto.decrypt(
    blob,
    "password1"
)`;

function qs<T extends Element = Element>(root: ParentNode, sel: string): T | null {
  return root.querySelector(sel) as T | null;
}
function qsa<T extends Element = Element>(root: ParentNode, sel: string): T[] {
  return [...root.querySelectorAll(sel)] as T[];
}

function highlight(t: string): string {
  return t
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/\b(from|import)\b/g, '<span class="k1">$1</span>')
    .replace(/(b?"[^"]*")/g, '<span class="k2">$1</span>')
    .replace(/\b(AryaCrypt|encrypt|decrypt)\b/g, '<span class="k4">$1</span>');
}

/** Wire scroll / pipeline / terminal / visualizer animations for the landing page. */
export function useLandingEffects(rootRef: RefObject<HTMLElement | null>) {
  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    document.documentElement.classList.add('landing-active');

    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
    const cleanups: Array<() => void> = [];

    /* Wordmark letters */
    const wm = qs<HTMLElement>(root, '.wm');
    if (wm && !wm.childElementCount) {
      [...'ARYACRYPT'].forEach((c, i) => {
        const s = document.createElement('span');
        s.textContent = c;
        s.style.setProperty('--i', String(i));
        wm.appendChild(s);
      });
    }

    /* Mobile nav */
    const burger = qs<HTMLButtonElement>(root, '#burger');
    const links = qs<HTMLElement>(root, '#links');
    const closeNav = () => {
      burger?.classList.remove('o');
      links?.classList.remove('o');
      burger?.setAttribute('aria-expanded', 'false');
    };
    const onBurger = () => {
      const o = burger?.classList.toggle('o');
      links?.classList.toggle('o', Boolean(o));
      burger?.setAttribute('aria-expanded', String(Boolean(o)));
    };
    burger?.addEventListener('click', onBurger);
    qsa(root, '#links a').forEach((a) => a.addEventListener('click', closeNav));
    cleanups.push(() => {
      burger?.removeEventListener('click', onBurger);
      qsa(root, '#links a').forEach((a) => a.removeEventListener('click', closeNav));
    });

    /* Scroll progress + nav */
    const bar = qs<HTMLElement>(root, '#bar');
    const nav = qs<HTMLElement>(root, '#nav');
    let tick = false;
    const onScroll = () => {
      const h = document.documentElement;
      const max = h.scrollHeight - innerHeight;
      if (bar) bar.style.transform = `scaleX(${max > 0 ? scrollY / max : 0})`;
      nav?.classList.toggle('sc', scrollY > 20);
      tick = false;
    };
    const onScrollRaf = () => {
      if (!tick) {
        tick = true;
        requestAnimationFrame(onScroll);
      }
    };
    addEventListener('scroll', onScrollRaf, { passive: true });
    addEventListener('resize', onScroll);
    onScroll();
    cleanups.push(() => {
      removeEventListener('scroll', onScrollRaf);
      removeEventListener('resize', onScroll);
    });

    /* Reveal on scroll */
    const io = new IntersectionObserver(
      (es) =>
        es.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            io.unobserve(e.target);
          }
        }),
      { threshold: 0.15, rootMargin: '0px 0px -6% 0px' }
    );
    qsa(root, '.rv').forEach((el) => io.observe(el));
    cleanups.push(() => io.disconnect());

    /* Side dots */
    const dots = qsa<HTMLAnchorElement>(root, '#side a');
    const so = new IntersectionObserver(
      (es) =>
        es.forEach((e) => {
          if (e.isIntersecting) {
            const id = '#' + e.target.id;
            dots.forEach((d) => d.classList.toggle('on', d.getAttribute('href') === id));
          }
        }),
      { threshold: 0.35 }
    );
    dots.forEach((d) => {
      const t = qs(root, d.getAttribute('href') || '');
      if (t) so.observe(t);
    });
    cleanups.push(() => so.disconnect());

    /* Counters */
    if (!reduce) {
      const co = new IntersectionObserver(
        (es) =>
          es.forEach((e) => {
            if (!e.isIntersecting) return;
            co.unobserve(e.target);
            const el = e.target as HTMLElement;
            const end = Number(el.dataset.n);
            const sf = el.dataset.s || '';
            let t0: number | undefined;
            const f = (t: number) => {
              t0 = t0 ?? t;
              const p = Math.min((t - t0) / 1400, 1);
              el.textContent = Math.round(end * p).toLocaleString('en-US') + sf;
              if (p < 1) requestAnimationFrame(f);
            };
            requestAnimationFrame(f);
          }),
        { threshold: 0.6 }
      );
      qsa(root, '[data-n]').forEach((el) => co.observe(el));
      cleanups.push(() => co.disconnect());
    }

    /* Cursor glow, magnetic buttons, tilt */
    if (fine && !reduce) {
      const g = qs<HTMLElement>(root, '#glow');
      const onMove = (e: PointerEvent) => {
        if (g) {
          g.style.left = e.clientX + 'px';
          g.style.top = e.clientY + 'px';
        }
      };
      addEventListener('pointermove', onMove, { passive: true });
      cleanups.push(() => removeEventListener('pointermove', onMove));

      qsa<HTMLElement>(root, '.mag').forEach((b) => {
        const move = (e: PointerEvent) => {
          const r = b.getBoundingClientRect();
          b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.12}px,${(e.clientY - r.top - r.height / 2) * 0.2}px)`;
        };
        const leave = () => {
          b.style.transform = '';
        };
        b.addEventListener('pointermove', move);
        b.addEventListener('pointerleave', leave);
        cleanups.push(() => {
          b.removeEventListener('pointermove', move);
          b.removeEventListener('pointerleave', leave);
        });
      });

      qsa<HTMLElement>(root, '.tilt').forEach((c) => {
        const move = (e: PointerEvent) => {
          const r = c.getBoundingClientRect();
          const x = (e.clientX - r.left) / r.width - 0.5;
          const y = (e.clientY - r.top) / r.height - 0.5;
          c.style.transform = `translateY(-8px) rotateX(${(-y * 5).toFixed(2)}deg) rotateY(${(x * 6).toFixed(2)}deg)`;
        };
        const leave = () => {
          c.style.transform = '';
        };
        c.addEventListener('pointermove', move);
        c.addEventListener('pointerleave', leave);
        cleanups.push(() => {
          c.removeEventListener('pointermove', move);
          c.removeEventListener('pointerleave', leave);
        });
      });
    }

    /* Hero particles */
    const cv = qs<HTMLCanvasElement>(root, '#cv');
    const hero = qs(root, '#hero');
    if (cv && hero && !reduce) {
      const cx = cv.getContext('2d');
      if (cx) {
        let P: Array<{ x: number; y: number; vx: number; vy: number; r: number }> = [];
        let W = 0;
        let H = 0;
        let vis = true;
        let raf = 0;
        const size = () => {
          const d = Math.min(devicePixelRatio || 1, 2);
          W = cv.clientWidth;
          H = cv.clientHeight;
          cv.width = W * d;
          cv.height = H * d;
          cx.setTransform(d, 0, 0, d, 0, 0);
          const n = Math.round(Math.min(70, (W * H) / 20000));
          P = Array.from({ length: n }, () => ({
            x: Math.random() * W,
            y: Math.random() * H,
            vx: (Math.random() - 0.5) * 0.18,
            vy: (Math.random() - 0.5) * 0.18,
            r: Math.random() * 1.2 + 0.5,
          }));
        };
        const draw = () => {
          if (!vis) return;
          cx.clearRect(0, 0, W, H);
          for (let i = 0; i < P.length; i++) {
            const a = P[i];
            a.x += a.vx;
            a.y += a.vy;
            if (a.x < 0 || a.x > W) a.vx *= -1;
            if (a.y < 0 || a.y > H) a.vy *= -1;
            cx.fillStyle = 'rgba(56,189,248,.45)';
            cx.beginPath();
            cx.arc(a.x, a.y, a.r, 0, 6.283);
            cx.fill();
            for (let j = i + 1; j < P.length; j++) {
              const b = P[j];
              const dx = a.x - b.x;
              const dy = a.y - b.y;
              const d = dx * dx + dy * dy;
              if (d < 14000) {
                cx.strokeStyle = `rgba(14,165,233,${0.12 * (1 - d / 14000)})`;
                cx.beginPath();
                cx.moveTo(a.x, a.y);
                cx.lineTo(b.x, b.y);
                cx.stroke();
              }
            }
          }
          raf = requestAnimationFrame(draw);
        };
        size();
        draw();
        const onResize = () => size();
        addEventListener('resize', onResize);
        const po = new IntersectionObserver((e) => {
          vis = e[0].isIntersecting;
          if (vis) {
            cancelAnimationFrame(raf);
            draw();
          }
        });
        po.observe(hero);
        cleanups.push(() => {
          cancelAnimationFrame(raf);
          removeEventListener('resize', onResize);
          po.disconnect();
        });
      }
    }

    /* Pipeline loop */
    const pl = qs<HTMLElement>(root, '#pl');
    const nds = pl ? qsa<HTMLElement>(pl, '.nd') : [];
    const pk = qs<HTMLElement>(root, '#pk');
    let cur = 0;
    let timer: ReturnType<typeof setInterval> | undefined;
    const place = (i: number) => {
      if (!pl || !pk || !nds[i]) return;
      const n = nds[i];
      const t = n.offsetTop + 10;
      const l = n.offsetLeft + n.offsetWidth / 2 - 5;
      const vert = getComputedStyle(pl).flexDirection === 'column';
      pk.style.transform = vert
        ? `translate(${n.offsetLeft - 17}px,${n.offsetTop + 22}px)`
        : `translate(${l}px,${t - 18}px)`;
    };
    const activate = (i: number) => {
      cur = i;
      nds.forEach((n, k) => n.classList.toggle('on', k === i));
      place(i);
    };
    const loop = () => activate((cur + 1) % nds.length);
    nds.forEach((n, i) =>
      n.addEventListener('click', () => {
        activate(i);
        clearInterval(timer);
        timer = setInterval(loop, 2600);
      })
    );
    if (pl) {
      const pio = new IntersectionObserver((e) => {
        clearInterval(timer);
        if (e[0].isIntersecting) {
          activate(cur);
          timer = setInterval(loop, 2600);
        }
      });
      pio.observe(pl);
      const onResize = () => place(cur);
      addEventListener('resize', onResize);
      activate(0);
      cleanups.push(() => {
        clearInterval(timer);
        pio.disconnect();
        removeEventListener('resize', onResize);
      });
    }

    /* Terminal typing + copy */
    const code = qs<HTMLElement>(root, '#code');
    const term = qs(root, '.term');
    const copyBtn = qs<HTMLButtonElement>(root, '#copy');
    let typed = false;
    if (code && term) {
      const to = new IntersectionObserver(
        (e, o) => {
          if (!e[0].isIntersecting || typed) return;
          typed = true;
          o.disconnect();
          if (reduce) {
            code.innerHTML = highlight(CODE_SRC);
            return;
          }
          let i = 0;
          const step = () => {
            i += 2;
            code.innerHTML = highlight(CODE_SRC.slice(0, i));
            if (i < CODE_SRC.length) setTimeout(step, 24);
          };
          step();
        },
        { threshold: 0.4 }
      );
      to.observe(term);
      cleanups.push(() => to.disconnect());
    }
    if (copyBtn) {
      const onCopy = async () => {
        try {
          await navigator.clipboard.writeText(CODE_SRC);
          copyBtn.textContent = 'Copied';
        } catch {
          copyBtn.textContent = 'Press Ctrl+C';
        }
        setTimeout(() => {
          copyBtn.textContent = 'Copy';
        }, 1600);
      };
      copyBtn.addEventListener('click', onCopy);
      cleanups.push(() => copyBtn.removeEventListener('click', onCopy));
    }

    /* Encryption visualizer */
    const rows = qsa<HTMLElement>(root, '.row');
    const arws = qsa<HTMLElement>(root, '.arw');
    const mt = qs<HTMLElement>(root, '#mt');
    const mst = qs<HTMLElement>(root, '#mst');
    const mock = qs(root, '#mock');
    const ICON = { done: '✓', act: '●', idle: '○' } as const;
    let a = 0;
    let mtimer: ReturnType<typeof setInterval> | undefined;
    let mrun = false;
    const paint = (active: number) => {
      rows.forEach((r, i) => {
        const s = i < active ? 'done' : i === active ? 'act' : 'idle';
        r.className = 'row ' + (s === 'idle' ? '' : s);
        const ic = r.firstChild as HTMLElement | null;
        if (ic) ic.textContent = ICON[s];
      });
      arws.forEach((w, i) => w.classList.toggle('f', i < active));
      if (mt) {
        mt.style.transform = `scaleX(${Math.min(1, (active + (active < rows.length ? 0.5 : 0)) / rows.length)})`;
      }
      if (mst) mst.textContent = active >= rows.length ? 'COMPLETE' : 'RUNNING';
    };
    const mstep = () => {
      paint(a);
      a++;
      if (a > rows.length + 1) {
        a = 0;
        if (mt) mt.style.transform = 'scaleX(0)';
      }
    };
    if (mock) {
      const mio = new IntersectionObserver(
        (e) => {
          if (e[0].isIntersecting && !mrun) {
            mrun = true;
            if (reduce) {
              paint(rows.length);
              return;
            }
            mstep();
            mtimer = setInterval(mstep, 1100);
          } else if (!e[0].isIntersecting && mrun && !reduce) {
            mrun = false;
            clearInterval(mtimer);
            a = 0;
            paint(-1);
          }
        },
        { threshold: 0.4 }
      );
      mio.observe(mock);
      cleanups.push(() => {
        clearInterval(mtimer);
        mio.disconnect();
      });
    }

    return () => {
      document.documentElement.classList.remove('landing-active');
      cleanups.forEach((fn) => fn());
    };
  }, [rootRef]);
}
