# Development

This is the place for development notes.

## Development environment

To develop ppf.docmap you will need:

```
pip install .[test]
pip install .[dev]
```

(Note: Depending or your shell, you will need to escape '[' and ']'.)

If you use conda, additionally install:

```
pip install .[dev-conda]
```

## The FileScanner-Registry

ppf.docmap keeps a registry of FileScanner classes. FileScanner classes are
children of the class FileScanner. Every child of the FileScanner class is
registered *automatically* as soon as the class is defined, i.e., as soon
as you define something like this

```
class MyScanner(FileScanner):
    pass
```

the code to register this class runs.

This is accomplished by using the
[registry pattern](https://charlesreid1.github.io/python-patterns-the-registry.html).
In python, everything is an object. Even classes - and by classes I am
referring to classes, not the *instances* of classes. Classes are instances
of the metaclass 'type':

```
class MyClass:
    pass

instance = MyClass

type(instance)
> __main__.MyClass

type(MyClass)
> type
```

When you create an instance of a class, ```__new__(...)``` of the class is
called. Correspondingly, when you create an instance of a metaclass, 
```__new__(...)``` of the metaclass runs. Therefore, we simply need to
modify ```type__new__(...)``` to run our registration code. Now, python
does not allow this. But we can do this:

```
class Registry(type):
    def __new__(cls, name, bases, attrs):
        do something


class FileScanner(metaclass=Registry):
    pass
```

Here, Registry is a (new) metaclass. FileScanner is a normal class but
it does not inherit from the usual metaclass (type) but from our new metaclass
Registry. Note the ```metaclass=Registry``` in the definition of FileScanner.

Now, as soon as python reads the definition of FileScanner it creates an
instance of its metaclass, i.e., an instance of ```Registry```. The same
will happen for every child of FileScanner.

Now, we implement the registry as follows:

```
class Registry(type):
    registry = {}

    def __new__(cls, name, bases, attrs):
        new_cls = super(Registry, cls).__new__(cls, name, bases, attrs)
        cls.registry[new_cls.mimetype] = new_cls

        return new_cls


class FileScanner(metaclass=Registry):
    mimetype = '*'


class DOCXScanner(FileScanner):
    mimetype = 'application/vnd.openxmlformats-officedocument'

    def __call__(self, url):
        # scan a docx file
        pass
```

The registry as an attribute of the metaclass: ```Registry.registry```.
```Registry.__new__(...)``` creates the new class ```new_cls```, looks
at its 'mimetype' class attribute, and adds mimetype:new_cls to the registry.

When defining a FileScanner class for a new document type (such as
DOCXScanner), we simply make it a child of FileScanner and set its mimetype
class attribute to the mimetype it is responsible for.

Note that it does not matter who defines children of FileScanner: It works
for classes defined from within ppf.docmap, but it also works for classes
defined elsewhere: If someone needs a FileScanner for a document type not
supported by ppf.docmap, he simply defines a new class which will register
itself in ```Registry.registry```. And from then on, ppf.docmap will be
able to scan this new document type.
