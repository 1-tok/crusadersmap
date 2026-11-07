"""A cairo.Context wrapper that splits one drawing into a picture pass and a lettering pass.

mode "pic":  lettering is skipped, everything else is drawn.
mode "text": only lettering is drawn (as outlines); everything else is skipped.
"""
import cairo

_DRAW = {"fill", "stroke", "fill_preserve", "stroke_preserve", "paint", "paint_with_alpha", "mask", "mask_surface"}


class SplitCtx:
    def __init__(self, ctx, mode):
        self._c = ctx
        self._mode = mode
        self._txt = False

    def __getattr__(self, name):
        real = getattr(self._c, name)
        if self._mode == "pic":
            if name in ("text_path", "show_text", "show_glyphs", "glyph_path"):
                return lambda *a, **k: None
            return real
        # text mode
        if name == "text_path":
            def tp(s):
                try:
                    cp = self._c.get_current_point()
                except Exception:
                    cp = (0, 0)
                if not self._txt:
                    self._c.new_path()
                    self._c.move_to(*cp)
                self._txt = True
                self._c.text_path(s)
            return tp
        if name == "show_text":
            def st(s):
                cp = self._c.get_current_point()
                self._c.new_path(); self._c.move_to(*cp)
                self._c.text_path(s); self._c.fill()
            return st
        if name == "clip" or name == "clip_preserve":
            return lambda *a, **k: self._c.new_path()
        if name == "new_path":
            def np_(*a):
                self._txt = False
                return self._c.new_path()
            return np_
        if name in _DRAW:
            def d(*a, **k):
                keep = name.endswith("preserve")
                if not self._txt:
                    if not keep:
                        self._c.new_path()
                    return
                r = real(*a, **k)
                if not keep:
                    self._txt = False
                return r
            return d
        return real
