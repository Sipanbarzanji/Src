# imports
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from random import choice, randint, sample

from .models import (
    workspace,
    workspace_members,
    project,
    tasks,
    label,
)
class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")

    first_name = factory.Faker("first_name")

    last_name = factory.Faker("last_name")

    email = factory.LazyAttribute(
        lambda obj: f"{obj.username}@example.com"
    )

    password = factory.PostGenerationMethodCall(
        "set_password",
        "Test123456"
    )


class WorkspaceFactory(DjangoModelFactory):

    class Meta:
        model = workspace

    name = factory.Sequence(
        lambda n: f"Workspace {n}"
    )

    description = factory.Faker(
        "text",
        max_nb_chars=150
    )

    owner = factory.SubFactory(UserFactory)


class WorkspaceMemberFactory(DjangoModelFactory):

    class Meta:
        model = workspace_members

    workspace = factory.SubFactory(
        WorkspaceFactory
    )

    user = factory.SubFactory(
        UserFactory
    )

    role = factory.LazyFunction(
        lambda: choice(["OW", "AD", "Mb"])
    )


class ProjectFactory(DjangoModelFactory):

    class Meta:
        model = project

    name = factory.Sequence(
        lambda n: f"Project {n}"
    )

    description = factory.Faker(
        "text",
        max_nb_chars=150
    )

    workspace = factory.SubFactory(
        WorkspaceFactory
    )

    create_by = factory.SubFactory(
        UserFactory
    )

    status = factory.LazyFunction(
        lambda: choice(["pn", "ac", "cp"])
    )


class TaskFactory(DjangoModelFactory):

    class Meta:
        model = tasks

    title = factory.Sequence(
        lambda n: f"Task {n}"
    )

    description = factory.Faker(
        "text",
        max_nb_chars=150
    )

    project = factory.SubFactory(
        ProjectFactory
    )

    assign = factory.SubFactory(
        UserFactory
    )

    create_by = factory.SubFactory(
        UserFactory
    )

    status = factory.LazyFunction(
        lambda: choice(["td", "ip", "rw", "dn"])
    )

    priority = factory.LazyFunction(
        lambda: choice(["lw", "md", "hg", "nc"])
    )

    deadline = factory.Faker(
        "date_time"
    )

LABEL_CHOICES = [
        "bg",
        "fe",
        "bk",
        "fn",
        "ur",
        "db",
    ]
class LabelFactory(DjangoModelFactory):

    class Meta:
        model = label

    name = factory.LazyFunction(
        lambda: choice(LABEL_CHOICES)
    )

    @factory.post_generation
    def task_table(self, create, extracted, **kwargs):

        if not create:
            return

        if extracted:
            for task in extracted:
                self.task_table.add(task)
def create():

    # -------------------------
    # Users
    # -------------------------

    users = UserFactory.create_batch(30)


    # -------------------------
    # Workspaces
    # -------------------------

    workspaces = WorkspaceFactory.create_batch(8)


    # -------------------------
    # Members
    # -------------------------

    for ws in workspaces:

        # Owner
        WorkspaceMemberFactory(
            workspace=ws,
            user=ws.owner,
            role="OW"
        )

        # انتخاب 4 تا 7 عضو غیر Owner
        available_users = [
            user for user in users
            if user != ws.owner
        ]

        selected_users = sample(
            available_users,
            randint(4, 7)
        )

        for user in selected_users:

            WorkspaceMemberFactory(
                workspace=ws,
                user=user,
                role=choice(["AD", "Mb"])
            )


    # -------------------------
    # Projects
    # -------------------------

    projects = []

    for ws in workspaces:

        for _ in range(4):

            project = ProjectFactory(
                workspace=ws,
                create_by=ws.owner
            )

            projects.append(project)


    # -------------------------
    # Tasks
    # -------------------------

    tasks_list = []

    for project in projects:

        members = list(
            project.workspace.workspace_member.all()
        )

        for _ in range(5):

            member = choice(members)

            task = TaskFactory(
                project=project,
                assign=member.user,
                create_by=project.create_by
            )

            tasks_list.append(task)


    # -------------------------
    # Labels
    # -------------------------

    labels = [
        LabelFactory(name=label_name)
        for label_name in LABEL_CHOICES
    ]

    # -------------------------
    # Assign Labels
    # -------------------------

    # اول تضمین می‌کنیم هر Label حداقل یک بار استفاده شود

    shuffled_tasks = tasks_list.copy()

    from random import shuffle

    shuffle(shuffled_tasks)

    for label_obj, task in zip(
        labels,
        shuffled_tasks
    ):

        label_obj.task_table.add(task)


    # بعد برای هر Task بین 1 تا 3 Label تصادفی
    for task in tasks_list:

        number_of_labels = randint(1, 3)

        selected_labels = sample(
            labels,
            number_of_labels
        )

        for label_obj in selected_labels:

            label_obj.task_table.add(task)


    print(
        "Fake data created successfully!"
    )