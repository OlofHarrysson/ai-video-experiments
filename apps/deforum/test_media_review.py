import unittest
from media_review import validate_session, same_timeline, fragment, check_inline_size

class ReviewTests(unittest.TestCase):
    def test_selection_validation(self):
        data = {'clips':[{'id':'a'}, {'id':'b'}], 'selected':['a','b']}
        self.assertEqual(validate_session(data), ['a','b'])
        for selected in ([], ['a','a'], ['missing'], ['a','b','a','b']):
            with self.assertRaises(ValueError):
                validate_session({**data, 'selected':selected})

    def test_refuses_dropped_or_retimed_frames(self):
        info = {'frame_count':3, 'frames':[{'time_seconds':t} for t in (0,.04,.12)]}
        same_timeline(info, info)
        for changed in ({'frame_count':2, 'frames':info['frames'][:2]},
                        {'frame_count':3, 'frames':[{'time_seconds':t} for t in (0,.04,.08)]}):
            with self.assertRaises(ValueError):
                same_timeline(info, changed)

    def test_labels_cannot_break_out_of_json_script(self):
        text = fragment({'label':'</script><img src=x onerror=alert(1)>'})
        self.assertNotIn('</script><img', text)
        self.assertIn('\\u003c/script>', text)

    def test_inline_budget_is_bytes_not_characters(self):
        check_inline_size('x' * 999999)
        with self.assertRaises(ValueError):
            check_inline_size('é' * 500000)

if __name__ == '__main__':
    unittest.main()
