import unittest
import tempfile
import jobfile_generator

TEST_STRING=b"""## OPTSCRIPT here ##"""

class test_mapper(unittest.TestCase):
    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile()
        self.optscript = tempfile.NamedTemporaryFile()
        self.optscript.file.write(TEST_STRING)
        self.optscript.file.flush()
        self.jg = jobfile_generator.jobfile_generator({
            "job": {
                "job_options": {},
                "application": {},
                "optimization": {},
                "target": {
                    "job_scheduler_type": "torque",
                    "name": "hlrs_testbed"
                }
            }
        },
        self.outfile.name)

    def test_add_optscript(self):
        self.jg.add_optscript(self.optscript.name, "file://" + self.optscript.name)

        # If everything worked correctly, our test line should have been
        # inserted into the output file by attempting to add an option script.
        self.outfile.file.seek(0)
        self.assertTrue(TEST_STRING in self.outfile.file.readlines())

    def test_add_optscript_bad_url(self):
        self.jg.add_optscript(self.optscript.name, "asdf://" + self.optscript.name)
        self.outfile.file.seek(0)
        self.assertIn(b"file=" + self.optscript.name.encode("UTF-8") + b"\n", self.outfile.file.readlines())

if __name__=="__main__":
    unittest.main()