from django.db import models
from django.forms import forms
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
import uuid  # Required for unique book instances
from datetime import date
from django.contrib.auth.models import User, AbstractUser  # Required to assign User as a borrower


# Create your models here.

class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        pass


class Cover(models.Model):
    def validate_image(value):
        size_limit = 2 * 1024 * 1024
        if value.size > size_limit:
            raise forms.ValidationError('Файл слишком большой. Размер файла не должен превышать 2MB')

    cover = models.ImageField(validators=[validate_image], upload_to='cover/books/title', verbose_name='Изображения',
                              blank=True, null=False)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Genre(models.Model):
    """Model representing a book genre (e.g. Science Fiction, Non Fiction)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)"
    )

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    objects = None
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    # ManyToManyField used because a genre can contain many books and a Book can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def validate_image(value):
        size_limit = 2 * 1024 * 1024
        if value.size > size_limit:
            raise forms.ValidationError('Файл слишком большой. Размер файла не должен превышать 2MB')

    photoPreview = models.ImageField(validators=[validate_image], upload_to='cover', verbose_name='Изображения',
                                     blank=False, null=True)
    bookFile = models.FileField(upload_to=' ', verbose_name='Файл с книгой', blank=False, null=True)

    class Meta:
        unique_together = ('title', 'author')
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def display_genre(self):
        """Creates a string for the Genre. This is required to display genre in Admin."""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def validate_image(value):
        size_limit = 2 * 1024 * 1024
        if value.size > size_limit:
            raise forms.ValidationError('Файл слишком большой. Размер файла не должен превышать 2MB')

    photo = models.ImageField(validators=[validate_image], upload_to='cover', verbose_name='Изображения',
                              blank=False, null=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Book availability')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        return '{0} ({1})'.format(self.id, self.book.title)


class Author(models.Model):
    """Model representing an author."""
    objects = None
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        unique_together = ('first_name', 'last_name', 'date_of_birth')
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return '{0}, {1}'.format(self.last_name, self.first_name)
