from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse as url_reverse
from model_utils.managers import InheritanceManager
from codeschool import models
from codeschool.shortcuts import delegation
from cs_courses.models import Discipline
from cs_activities.models import Activity, Response


class Question(models.TimeStampedModel, models.InheritableModel):
    """Base class for all question types"""

    title = models.CharField(
        _('title'),
        max_length=200,
    )
    short_description = models.CharField(
        _('short description'),
        max_length=140,
        help_text=_('A very brief one-phrase description used in listings.'),
    )
    long_description = models.TextField(
        _('long description'),
        help_text=_('A detailed explanation.')
    )
    author_name = models.CharField(
        _('Author\'s name'),
        max_length=100,
        blank=True,
    )
    comment = models.TextField(
        _('Comments'),
        blank=True,
        help_text=_('(Optional) Any private information that you want to '
                    'associate to the object.')
    )
    discipline = models.ForeignKey(
        Discipline,
        blank=True,
        null=True,
        help_text=_(
            'This optional field points to the discipline that is the relevant '
            'to question.'
        ),
    )
    owner = models.ForeignKey(
        models.User,
        blank=True,
        null=True,
        help_text=_('User who created or uploaded this question.')
    )
    is_active = models.BooleanField(
        _('is active'),
        default=False,
        blank=True,
        help_text=_(
            'Marks a question as active/inactive. Inactive questions are not'
            'shown publicly and are only available to the question owner.'
        )
    )

    # Manager
    objects = InheritanceManager()
    response_cls = Response
    default_extension = '.md'

    # Properties
    @property
    def unbound_responses(self):
        return getattr(self, self.response_cls.__name__.lower() + '_set')

    class Meta:
        permissions = (("download_question", "Can download question files"),)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return url_reverse('question-detail', args=(self.pk,))

    def update(self):
        """Tells question object to validate and update any fields necessary
        to fulfill the validation.

        The default implementation is empty. Subclasses may need to implement
        some special logic here.
        """

    def export(self, type=None):
        """Export question to the given data type.

        This method can return NotImplemented to tell that the designated data
        type is not supported."""

        return NotImplemented

    def grade(self, response):
        """Return a Feedback object to the given response."""

        return self.feedback_cls(response, self.answer == response.value)

    # Permission control
    def can_edit(self, user):
        """Only the owner of the question can edit it"""
        if user is None or self.owner is None:
            return False
        return self.owner.pk == user.pk

    def can_create(self, user):
        """You have to be the teacher of a course in order to create new
        questions."""

        return not user.courses_as_teacher.empty()


class QuestionActivity(Activity):
    """
    In this activity, students have to answer a single question.
    """
    question_base = models.ForeignKey(Question, related_name='activities')

    @property
    def question(self):
        return self.question_base.as_subclass()

    # Properties
    name = property(lambda x: x.question.name)
    short_description = property(lambda x: x.question.short_description)
    long_description = property(lambda x: x.question.long_description)

    # Fetching responses
    def retroact_question_responses(self):
        """Use all question responses that are unlinked to an activity and
        create responses bounded to the given activity. These responses create
        a reference to the original response in the `parent` attribute."""

        question = self.question_base
        activities = question.activities.all()
        responses = Response.objects.filter(activity__in=activities)
        unbound = question.unbound_responses.all()
        retroacted = responses.filter(parent__in=unbound)
        missing = unbound.exclude(retroacted.select_related('parent'))


class QuestionResponse(Response):
    class Meta:
        abstract = True

    question_for_unbound = models.ForeignKey(
        Question,
        blank=True, null=True,
        help_text='Question object reference for unbound responses. This '
                  'should be null for activity responses.'
    )

    @property
    def question_base(self):
        """The base question object.

        The base question is a cs_question.Question instance and therefore do
        not implement the full interface of the real question object.

        It will use either question_for_unbound or activity.question."""

        return (self.question_for_unbound or
                self.activity.questionactivity.question_base)

    @question_base.setter
    def question_base(self, value):
        if self.activity is None:
            self.question_for_unbound = value
        elif self.question_base.pk != value.pk:
            raise AttributeError(
                'Cannot set the "question" attribute in activity-based '
                'responses'
            )

    @property
    def question(self):
        """The question object instantiated as the correct Question subclass."""

        return self.question_base.as_subclass()

    @question.setter
    def question(self, value):
        if type(value) is Question:
            self.question_base = value
        else:
            self.question_base = value.question_ptr


#
# Derived question types
#
class FreeAnswerQuestion(Question):
    DATA_FILE = 'file'
    DATA_IMAGE = 'image'
    DATA_PDF = 'pdf'
    DATA_PLAIN = 'plain'
    DATA_RICHTEXT = 'richtext'
    DATA_CHOICES = (
        (DATA_FILE, _('Arbitary file')),
        (DATA_IMAGE, _('Image file')),
        (DATA_PDF, _('PDF file')),
        (DATA_RICHTEXT, _('Rich text input')),
        (DATA_RICHTEXT, _('Plain text input')),
    )
    metadata = models.TextField()
    data_type = models.CharField(choices=DATA_CHOICES, max_length=10)
    data_file = models.FileField(blank=True, null=True)


class NumericResponse(QuestionResponse):
    value = models.FloatField(
        _('Value'),
        help_text=_('Result (it must be a number)')
    )

    def autograde(self):
        self.feedback_data = self.value

    def get_grade_from_feedback(self):
        question = self.question
        if abs(self.feedback_data - question.answer) <= question.tolerance:
            return 100
        else:
            return 0


class NumericQuestion(Question):
    answer = models.FloatField(
        _('Answer'),
        help_text=_('The numeric value for the correct answer')
    )
    tolerance = models.FloatField(
        _('Tolerance'),
        help_text=_('If given, defines the tolerance within responses are '
                    'still considered to be correct'),
        default=0,
        blank=True,
    )

    response_cls = NumericResponse

    @property
    def is_exact(self):
        return self.tolerance == 0

    @property
    def start(self):
        return self.answer - abs(self.tolerance)

    @property
    def end(self):
        return self.answer + abs(self.tolerance)

    @property
    def range(self):
        return self.start, self.end

    def grade(self, response):
        x, y = self.range
        response.grade = (100 if x <= response.value <= y else 0)
        response.save()


class BooleanQuestion(Question):
    answer = models.BooleanField()


class StringMatchQuestion(Question):
    answer = models.TextField()
    is_regex = models.BooleanField(default=True)

    def grade(self, response):
        if self.is_regex:
            value = response.value

        else:
            return super().grade(response)

# Import other question types
from cs_questions.models_io import *
