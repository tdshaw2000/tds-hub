import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import tempfile  # noqa: E402

from check_site import check_apps, check_index, check_launcher, main  # noqa: E402

GOOD = {"name": "A", "url": "https://a.duckdns.org", "description": "d", "icon": "🔗"}


class CheckApps(unittest.TestCase):
    def test_a_valid_list_has_no_problems(self):
        self.assertEqual(check_apps([GOOD]), [])

    def test_icon_is_optional(self):
        app = {k: v for k, v in GOOD.items() if k != "icon"}
        self.assertEqual(check_apps([app]), [])

    def test_empty_or_non_list_is_rejected(self):
        self.assertTrue(check_apps([]))
        self.assertTrue(check_apps({"name": "A"}))

    def test_missing_or_blank_required_fields_are_rejected(self):
        for key in ("name", "url", "description"):
            with self.subTest(key=key):
                self.assertTrue(check_apps([{**GOOD, key: "  "}]))
                self.assertTrue(check_apps([{k: v for k, v in GOOD.items() if k != key}]))

    def test_url_must_be_absolute_https(self):
        for url in ("http://a.duckdns.org", "a.duckdns.org", "https://", "javascript:alert(1)"):
            with self.subTest(url=url):
                self.assertTrue(check_apps([{**GOOD, "url": url}]))

    def test_duplicate_names_are_rejected_case_insensitively(self):
        self.assertTrue(check_apps([GOOD, {**GOOD, "name": "a"}]))

    def test_duplicate_names_ignore_surrounding_whitespace(self):
        self.assertTrue(check_apps([GOOD, {**GOOD, "name": " A "}]))

    def test_unknown_keys_are_rejected(self):
        self.assertTrue(check_apps([{**GOOD, "desc": "typo"}]))


class CheckIndex(unittest.TestCase):
    def site(self, html, files=()):
        folder = Path(tempfile.mkdtemp())
        (folder / "index.html").write_text(html)
        for name in files:
            (folder / name).write_text("")
        return folder

    def test_a_missing_linked_file_is_reported(self):
        site = self.site('<link href="style.css"><script src="app.js"></script>', ["app.js"])
        self.assertEqual(check_index(site), ["index.html refers to missing style.css"])

    def test_root_relative_links_resolve_inside_the_site(self):
        site = self.site('<link href="/style.css">', ["style.css"])
        self.assertEqual(check_index(site), [])

    def test_external_links_are_ignored(self):
        self.assertEqual(check_index(self.site('<a href="https://example.org">x</a>')), [])


class CheckLauncher(unittest.TestCase):
    def script(self, body):
        path = Path(tempfile.mkdtemp()) / "launcher.sh"
        path.write_text(body)
        return path

    def test_a_bash_syntax_error_is_reported(self):
        self.assertTrue(check_launcher(self.script("if true; then\n")))

    def test_valid_bash_passes(self):
        self.assertEqual(check_launcher(self.script("echo ok\n")), [])


class Repo(unittest.TestCase):
    def test_the_repo_itself_passes(self):
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
