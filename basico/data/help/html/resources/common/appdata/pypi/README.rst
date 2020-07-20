About KB4IT
===========

Introduction
^^^^^^^^^^^^

*KB4IT* is a static website generator based on Asciidoctor sources mainly
for technical documentation purposes.

You can see some demos here: https://github.com/t00m/kb4it-adocs

Motivations
^^^^^^^^^^^
-  The main aim is to provide an easy way to write my technical documentation.
-  Don't care about the formatting and focus on the contents.
-  To allow teams to manage their knowledge database easily.
-  Do not depend on third software products like word processors or complex web applications.

Features
^^^^^^^^

Pros
""""

- Writing documentation: Documents must be in Asciidoctor format which is easy to learn.
- Finding documents: Once a document is converted to html, properties can be browsed. Moreover, property pages have filters and a search entry to filter by title.
- Publishing your repository: all necessary files are inside a directory. Browse it or copy it to your web server.
- Serverless: There is no need for a web server. Of course, you can use one if you please.
- Smart compiling: Only those documents added or modified are compiled.
- Use the default themes or build your own custom theme
- By modifying templates, it might be integrated with Github or Gitlab.

Cons
""""

- Not to much documentation at this moment
- No online editor: At this moment, KB4IT doesn't include any online editor. You must create or edit your documents with your preferred editor.
- No dynamic search: KB4IT was developed to be as simple as possible.
- No dependencies at all excepting Asciidoctor (as text processor and publishing toolchain) and Python (the programming language used).
- API is not stable
- Most of the requirements are tailored to my own necessities which might not be the same as yours.

Installation
^^^^^^^^^^^^

From source
"""""""""""

If you have used this app before, it might be necessary to uninstall it before:

``pip3 uninstall kb4it -qy``

Then, install it:

``python3 setup.py install --user``

Pypi package
""""""""""""

``pip3 install kb4it --user -U``

Execution
^^^^^^^^^

The most typical usage would be:

``$HOME/.local/bin/kb4it -source /path/to/asciidoctor/sources -target /path/to/target/directory -log DEBUG``

If templates remain the same, force a new compilation:

``$HOME/.local/bin/kb4it -source /path/to/asciidoctor/sources -target /path/to/target/directory --log DEBUG  -force``

If the directory containing the asciidoctor sources have a theme, it will be used. However, you can specify one:


``$HOME/.local/bin/kb4it -source /path/to/asciidoctor/sources -target /path/to/target/directory -theme mytheme -log DEBUG``


You can also specify any_datetime_attribute to sort your documents:

``$HOME/.local/bin/kb4it -source /path/to/asciidoctor/sources -target /path/to/target/directory -sort Published -log DEBUG``


Download
^^^^^^^^

Get the code  from Github: https://github.com/t00m/KB4IT

``git clone https://github.com/t00m/KB4IT``


Credits
^^^^^^^

-  `Python <http://www.python.org/>`_ Programming language that lets you work more quickly and integrate your systems more effectively.
-  `Asciidoctor <https://asciidoctor.org>`_ A fast text processor & publishing toolchain for converting AsciiDoc to HTML5, DocBook & more.
-  `UIKit <https://getuikit.com>`_ A lightweight and modular front-end framework for developing fast and powerful web interfaces.
-  `Geany <https://www.geany.org/>`_ Powerful, stable and lightweight programmer's text editor that provides tons of useful features without bogging down your workflow. It runs on Linux, Windows and MacOS is translated into over 40 languages, and has built-in support for more than 50 programming languages.


Contact
^^^^^^^

Tomás Vírseda (aka t00m): tomasvirseda@gmail.com

*I would appreciate to hear from your comments.*
