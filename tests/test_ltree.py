from string import ascii_lowercase, ascii_uppercase, digits

from ltree import Ltree


class TestInit:
    def test_from_string(self):
        t = Ltree("foo.bar.baz")
        assert type(t) is Ltree
        assert len(t) == 3
        assert t == "foo.bar.baz"

    def test_from_args(self):
        t = Ltree("foo", 42, None, "baz")
        assert type(t) is Ltree
        assert len(t) == 3
        assert t == "foo.42.baz"

    def test_from_sequence(self):
        t = Ltree(["foo", 42, None, "baz"])
        assert type(t) is Ltree
        assert len(t) == 3
        assert t == "foo.42.baz"

    def test_from_ltree(self):
        t = Ltree("foo.bar.baz")
        t = Ltree(t)
        assert type(t) is Ltree
        assert len(t) == 3
        assert t == "foo.bar.baz"

    def test_from_sequences(self):
        t = Ltree("foo.bar", "baz.qux")
        assert len(t) == 4
        assert t == "foo.bar.baz.qux"

        t = Ltree("foo.bar", ["baz", None, 42])
        assert len(t) == 4
        assert t == "foo.bar.baz.42"

    def test_empty(self):
        t = Ltree()
        assert type(t) is Ltree
        len(t) == 0
        assert not t

        t = Ltree(None)
        assert type(t) is Ltree
        assert not t

        t = Ltree("")
        assert type(t) is Ltree
        assert not t

        t = Ltree([])
        assert type(t) is Ltree
        assert not t

    def test_valid(self):
        valid = ascii_lowercase + ascii_uppercase + digits + "_"
        for c in valid:
            t = Ltree(c)
            assert type(t) is Ltree
            assert t == c

        for i in range(256):
            c = chr(i)
            if c == ".":
                continue
            if c not in valid:
                try:
                    Ltree(c)
                except ValueError:
                    continue
                else:
                    assert False, "didn't raise: %s" % c


class TestRepr:
    def test_repr(self):
        assert type(repr(Ltree())) is str
        assert type(repr(Ltree("a"))) is str
        assert type(repr(Ltree("a.b"))) is str

        assert repr(Ltree()) == "Ltree('')"
        assert repr(Ltree("a")) == "Ltree('a')"
        assert repr(Ltree("a", "b")) == "Ltree('a.b')"

    def test_str(self):
        assert type(str(Ltree())) is str
        assert type(str(Ltree("a"))) is str
        assert type(str(Ltree("a", "b"))) is str

        assert str(Ltree()) == ""
        assert str(Ltree("a")) == "a"
        assert str(Ltree("a", "b")) == "a.b"


class TestOps:
    def test_eq(self):
        assert Ltree("a.b") == Ltree("a.b")
        assert Ltree("a.b") == "a.b"
        assert "a.b" == Ltree("a.b")

        assert Ltree("") == Ltree()
        assert Ltree("") == ()
        assert Ltree() == ""

    def test_ne(self):
        assert Ltree("a.b") != Ltree("a.b.c")
        assert "a.b" != Ltree("a.b.c")
        assert Ltree("a.b") != "a.b.c"

    def test_gt(self):
        assert Ltree("a.b") < Ltree("a.b.c")
        assert Ltree("a.b") <= Ltree("a.b.c")
        assert Ltree("a.b") < Ltree("a.c")
        assert Ltree("a.b") <= Ltree("a.c")
        assert Ltree("aa.b") > Ltree("a.c")
        assert Ltree("aa.b") >= Ltree("a.c")

    def test_add(self):
        assert Ltree("a.b") + "c" == Ltree("a.b.c")
        assert Ltree("a.b") + "" == Ltree("a.b")
        assert (Ltree("a.b") + None) == Ltree("a.b")
        assert Ltree("a.b") + 42 == Ltree("a.b.42")
        assert Ltree("a.b") + ["c", None, 42] == Ltree("a.b.c.42")

    def test_radd(self):
        assert "c" + Ltree("a.b") == Ltree("c.a.b")
        assert "" + Ltree("a.b") + "" == Ltree("a.b")
        assert (None + Ltree("a.b")) == Ltree("a.b")
        assert 42 + Ltree("a.b") + "" == Ltree("42.a.b")
        assert ["c", None, 42] + Ltree("a.b") == Ltree("c.42.a.b")

    def test_getitem(self):
        assert type(Ltree("a")[0]) is str

        lt = Ltree("foo.bar.baz")
        assert lt[0] == "foo"
        assert lt[1] == "bar"
        assert lt[2] == "baz"
        assert lt[-1] == "baz"
        assert lt[-2] == "bar"
        assert lt[-3] == "foo"

        for i in [3, 4, 5, -4, -5]:
            try:
                lt[i]
            except IndexError:
                pass
            else:
                assert False

    def test_slice(self):
        assert type(Ltree()[1:2]) is Ltree
        assert type(Ltree()[slice(1, 2)]) is Ltree

        lt = Ltree("foo.bar.baz")
        assert lt[0:3] == "foo.bar.baz"
        assert lt[1:2] == "bar"
        assert lt[1:] == "bar.baz"
        assert lt[:-1] == "foo.bar"
        assert lt[0:0] == ""
