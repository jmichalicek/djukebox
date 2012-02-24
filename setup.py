from setuptools import setup, find_packages

package_data = ['static/css/*', 'static/img/*', 'static/js/*', 'templates/*']
dependencies = ['South==0.7.3']
setup(name = "djukebox",
      version = "0.0.1",
      description = "A django HTML 5 audio player",
      author = "Justin Michalicek",
      author_email = "jmichalicek@gmail.com",
      url = "https://github.com/jmichalicek/djukebox/",
      packages = find_packages(),
      #'package' package must contain files (see list above)
      package_data = {'djukebox' : package_data },
      install_requires = dependencies,
      long_description = """Really long text here.""" 
      #This next part it for the Cheese Shop, look a little down the page.
      #classifiers = []     
)
