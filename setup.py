from setuptools import setup, find_packages

package_data = ['static/css/*', 'static/img/*', 'static/js/*', 'static/js/templates/*', 'templates/djukebox/*']
dependencies = ['pillow', 'django-celery==2.5.5', 'mutagen', 'simplejson', 'django-bootstrap-form', 'django-tastypie==0.9.11']
setup(name = "djukebox",
      version = "0.1.0",
      description = "A django HTML 5 audio player",
      author = "Justin Michalicek",
      author_email = "jmichalicek@gmail.com",
      url = "https://github.com/jmichalicek/djukebox/",
      license = "www.opensource.org/licenses/bsd-license.php",
      packages = find_packages(),
      #'package' package must contain files (see list above)
      package_data = {'djukebox' : package_data },
      install_requires = dependencies,
      long_description = """A HTML 5 audio player using Django"""
      #This next part it for the Cheese Shop, look a little down the page.
      #classifiers = []
)
