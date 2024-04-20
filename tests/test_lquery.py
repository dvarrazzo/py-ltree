from ltree import Star, Lquery


class TestStar:
    def test_parse(self):
        for a, b in [
            ("*", Star(None, None)),
            ("*{2}", Star(2, 2)),
            ("*{9999}", Star(9999, 9999)),
            ("*{,2}", Star(None, 2)),
            ("*{2,}", Star(2, None)),
            ("*{2,4}", Star(2, 4)),
            ("*{222,444}", Star(222, 444)),
        ]:
            try:
                s = Star.parse(a)
            except ValueError as e:
                assert False, "error parsing %r: %s" % (a, e)
            assert s == b

    def test_bad_parse(self):
        for (a,) in [
            ("*{}",),
            ("*{,,2}",),
            ("*{-9999}",),
            ("*{,2,}",),
            ("*{2,,}",),
        ]:
            try:
                s = Star.parse(a)
            except ValueError as e:
                assert False, "error parsing %r: %s" % (a, e)
            assert s is None

    def test_star_fusion_init(self):
        q = Lquery("foo.*.*.bar")
        assert q == "foo.*.bar"
        assert len(q) == 3

    def test_star_fusion_join(self):
        q = Lquery(["foo", "*{1}", "*{1}", "bar"])
        assert str(q) == "foo.*{2}.bar"

        q = Lquery(["foo", "*{1,2}", "*{3,}", "bar"])
        assert str(q) == "foo.*{4,}.bar"

    def test_rfusion(self):
        q = Lquery(["foo"])
        q += "bar"
        assert str(q) == "foo.bar"
        q += "*{2}"
        assert str(q) == "foo.bar.*{2}"
        q += "*{1}"
        assert str(q) == "foo.bar.*{3}"
        q += "baz"
        assert str(q) == "foo.bar.*{3}.baz"
        q += "*{1,1}"
        assert str(q) == "foo.bar.*{3}.baz.*{1}"
        q += "*{1}"
        assert str(q) == "foo.bar.*{3}.baz.*{2}"

    def test_or(self):
        assert str(Lquery(["foo|bar"])) == "foo|bar"
