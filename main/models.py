import datetime

from django.db import models


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Study(models.Model):
    study_number = models.IntegerField(unique=True)
    study_name = models.CharField(max_length=255, unique=True)
    missing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.study_number} ({self.study_name})"

    class Meta:
        verbose_name_plural = "studies"
        ordering = ["study_number"]

class Group(models.Model):
    group_number = models.IntegerField(unique=True)
    group_name = models.CharField(max_length=255, unique=True)
    missing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.group_number} ({self.group_name})"

    class Meta:
        ordering = ["group_number"]


class Instrument(models.Model):
    instrument_name = models.CharField(max_length=255, unique=True)
    # optionally include the label - i.e. the REDCap display name
    instrument_label = models.TextField(blank=True, null=True)
    instrument_field = models.CharField(max_length=255,
        help_text="An API record import must include at least one field, even if it's empty")

    def __str__(self):
        return self.instrument_name

    class Meta:
        ordering = ["instrument_name"]

# class StudyInstrument(models.Model):
#     study = models.ForeignKey("Study", on_delete=models.CASCADE)
#     instrument = models.ForeignKey("Instrument", on_delete=models.CASCADE)
#     min_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no min age")
#     max_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no max age")

class InstrumentCreationRule(models.Model):
    class StrictOperatorOptions(models.TextChoices):
        MIN = "min", "min"
        MAX = "max", "max"
        BOTH = "both", "both"
    
    study = models.ForeignKey("Study", on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.PROTECT, blank=True, null=True, help_text="Leave blank for all groups")
    min_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no min age")
    max_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no max age")
    strict_operator = models.BooleanField(blank=False, choices=((True, 'Yes'), (False, 'No')), help_text="Select Yes to make the operators strictly less than for max age and strictly greater than for min age.  Select No to include records equal to listed min or max age(s).")
    strict_operator_choice = models.CharField(max_length = 20, blank=True, null=True, choices=StrictOperatorOptions.choices)
    instruments = models.ManyToManyField("Instrument", blank=True, help_text="Hold ctrl to select multiple")

    def __str__(self):
        return f"rule #{self.id} - study: {self.study}"

    class Meta:
        ordering = ["study__study_name", "id"]

    def list_instruments(self):
        list = []
        for oInstrument in self.instruments.all():
            list.append(oInstrument.instrument_name)
        return ", ".join(list)

    def describe_rule(self):
        group_desc = ""
        min_age_desc = ""
        max_age_desc = ""
        if self.group:
            group_desc = f" and group is {self.group}"
        if self.strict_operator:
            if self.min_age:
                if self.strict_operator_choice and (self.strict_operator_choice == "min" or self.strict_operator_choice == "both"):
                    min_age_desc = f" and age > {self.min_age}"
            if self.max_age:
                if self.strict_operator_choice and (self.strict_operator_choice == "max" or self.strict_operator_choice == "both"):
                    max_age_desc = f" and age < {self.max_age}"
        elif not self.strict_operator:
            if self.min_age:
                min_age_desc = f" and age >= {self.min_age}"
            if self.max_age:
                max_age_desc = f" and age <= {self.max_age}"
        desc = f"if study is {self.study}{group_desc}{min_age_desc}{max_age_desc}"
        return desc







class CompletedVisit(TimeStampedModel):
    """
    Tracks which visit records have already been processed
    """
    record_id = models.CharField(max_length=255)
    instance = models.IntegerField()
    visit_date = models.DateField(blank=True, null=True)
    ignore = models.BooleanField(default=False, help_text="don't create instruments for this visit")

    class Meta:
        unique_together = (("record_id", "instance"),)
        ordering = ["record_id", "instance"]

    def __str__(self):
        return f"record_id {self.record_id}, instance {self.instance}"

class CreatedInstrument(models.Model):
    """
    Tracks all the instruments that were created for a visit
    """
    visit = models.ForeignKey(CompletedVisit, on_delete=models.CASCADE)
    instrument_name = models.CharField(max_length=255)
    instance = models.IntegerField()
    successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        response = f"record_id {self.visit.record_id}, instrument {self.instrument_name}, instance {self.instance}"
        if self.successful:
            return response
        return "(FAILED) " + response

class InstrumentCreationEventLog(models.Model):
    """ Tracks calls to function create_instruments_for_all_incomplete().

    The main purpose of tracking this is to prevent the method from being called twice at the
    same time. Doing so could result in duplicate instruments being created.
    """
    class StatusOptions(models.TextChoices):
        STARTED = "started", "started"
        FINISHED = "finished", "finished"
        NEVER_FINISHED = "never_finished", "never_finished"

    status = models.CharField(max_length=20, choices=StatusOptions.choices, default=StatusOptions.STARTED,)
    start = models.DateTimeField()
    finish = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    @staticmethod
    def flag_never_finished():
        """
        If a started event takes too long, it should be assumed to have failed and flagged as
        "never_finished".
        """
        qLog = InstrumentCreationEventLog.objects.filter(
            status=InstrumentCreationEventLog.StatusOptions.STARTED
        )
        assume_failed_minutes = 60      # assume an event failed after 60 minutes
        for oLog in qLog:
            time_delta = datetime.datetime.now() - oLog.start
            minutes = time_delta.total_seconds() / 60
            if minutes > assume_failed_minutes:
                oLog.status = InstrumentCreationEventLog.StatusOptions.NEVER_FINISHED
                oLog.comment = f"marked as never finished at {datetime.datetime.now()}"
                oLog.save()





