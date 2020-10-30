import pytest
from core import listdir, rename, Selection, changefn, FilenameCollisionError, prefixfn, suffixfn, insertfn, appendfn


def test_listdir(tmp_path):
    fs, ds = {'f1', 'f2', 'f3'}, {'d1', 'd2', 'd3'}
    for d in ds:
        (tmp_path / d).mkdir()
    for f in fs:
        (tmp_path / f).write_text('')
    assert set(listdir(tmp_path)) == fs


def test_rename(tmp_path):
    for f in {'a', 'b', 'c', 'd', 'e', 'f'}:
        (tmp_path / f).write_text('')
    count = rename(tmp_path, [('a', 'A'), ('b', 'B'), ('c', 'c'), ('d', 'd')])
    assert set(listdir(tmp_path)) == {'A', 'B', 'c', 'd', 'e', 'f'} and count == 2


@pytest.mark.parametrize("s, x, sx", [
    ('foo', 'd', 'dfoo'),
    ('foo', '', 'foo'),
])
def test_prefix(s, x, sx):
    assert prefixfn(s, '', x) == sx


@pytest.mark.parametrize("s, x, sx", [
    ('foo', 'd', 'food'),
    ('foo', '', 'foo'),
])
def test_suffix(s, x, sx):
    assert suffixfn(s, '', x) == sx


@pytest.mark.parametrize("s, ss, t, r", [
    ('abcd', 'bc', 'x', 'axbcd'),
    ('abcd', 'foo', 'x', 'abcd'),
    ('abcd', '', 'x', 'abcd'),
    ('abcd', 'bc', '', 'abcd'),
])
def test_insertfn(s, ss, t, r):
    assert insertfn(s, ss, t) == r


@pytest.mark.parametrize("s, ss, t, r", [
    ('abcd', 'bc', 'x', 'axd'),
    ('abcd', 'foo', 'x', 'abcd'),
    ('abcd', '', 'x', 'abcd'),
    ('abcd', 'bc', '', 'ad'),
])
def test_changefn(s, ss, t, r):
    assert changefn(s, ss, t) == r


@pytest.mark.parametrize("s, ss, t, r", [
    ('abcd', 'bc', 'x', 'abcxd'),
    ('abcd', 'foo', 'x', 'abcd'),
    ('abcd', '', 'x', 'abcd'),
    ('abcd', 'bc', '', 'abcd'),
])
def test_appendfn(s, ss, t, r):
    assert appendfn(s, ss, t) == r


@pytest.fixture
def selection():
    return Selection(['foo_123', 'foo_456', 'bar_123', 'baz_123'])


def test_everything_is_selected_by_default(selection):
    assert selection.active() == [0, 1, 2, 3]


def test_selections_can_by_refined_using_patterns(selection):
    selection.tighten('foo')
    assert selection.active() == [0, 1]


def test_selections_can_be_progressively_refined(selection):
    selection.tighten('123')
    selection.tighten('ba')
    assert selection.active() == [2, 3]


def test_invalid_patterns_result_in_empty_selections(selection):
    selection.tighten('hello')
    assert selection.active() == []


def test_selections_can_be_rolled_back(selection):
    selection.tighten('123')
    selection.tighten('ba')
    selection.loosen()
    assert selection.active() == [0, 2, 3]


def test_selections_can_be_resolved_to_filenames(selection):
    selection.tighten('ba')
    assert selection.peek() == [('bar_123', 'bar_123'), ('baz_123', 'baz_123')]


def test_selections_can_be_reset(selection):
    selection.tighten('ba')
    selection.tighten('z')
    selection.clear()
    assert selection.active() == [0, 1, 2, 3]


def test_selections_can_be_transformed(selection):
    selection.tighten('foo')
    selection.transform(lambda s: changefn(s, 'foo', 'FOO'))
    assert selection.peek() == [('foo_123', 'FOO_123'), ('foo_456', 'FOO_456')]


def test_transformations_can_be_undone(selection):
    selection.transform(lambda s: changefn(s, 'foo', 'FOO'))
    selection.rollback()
    assert [x for (_, x) in selection.peek()] == ['foo_123', 'foo_456', 'bar_123', 'baz_123']


def test_transformations_can_be_selectively_undone(selection):
    selection.transform(lambda s: changefn(s, 'foo', 'FOO'))
    selection.tighten('123')
    selection.rollback()
    selection.clear()
    assert [x for (_, x) in selection.peek()] == ['foo_123', 'FOO_456', 'bar_123', 'baz_123']


def test_transformations_are_aborted_on_filename_collisions(selection):
    with pytest.raises(FilenameCollisionError):
        selection.transform(lambda s: changefn(s, '123', '456'))
    assert [x for (_, x) in selection.peek()] == ['foo_123', 'foo_456', 'bar_123', 'baz_123']


def test_transformations_are_rolledback_only_for_modified_files(selection):
    selection.transform(lambda s: changefn(s, 'foo', 'FOO'))
    selection.tighten('foo')
    with pytest.raises(FilenameCollisionError):
        selection.transform(lambda s: changefn(s, 'FOO_123', 'bar_123'))
    assert [x for (_, x) in selection.peek()] == ['FOO_123', 'FOO_456']


def test_file_cannot_be_renamed_to_the_empty_string(selection):
    selection.transform(lambda s: changefn(s, 'foo_123', ''))
    assert [x for (_, x) in selection.peek()] == ['foo_123', 'foo_456', 'bar_123', 'baz_123']


def test_uncommitted_filenames_shouldnot_be_considered_for_selection(selection):
    selection.transform(lambda s: changefn(s, 'f', 'F'))
    selection.tighten('f')
    s1 = selection.peek()
    selection.clear()
    selection.tighten('F')
    s2 = selection.peek()
    assert s1 == [('foo_123', 'Foo_123'), ('foo_456', 'Foo_456')] and s2 == []
