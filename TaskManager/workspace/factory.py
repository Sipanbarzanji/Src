import random
import factory

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from factory.django import DjangoModelFactory

from .models import (
    workspace,
    workspace_members,
    project,
    tasks,
    label,
)


# =========================================================
# FACTORIES
# =========================================================

class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(
        lambda n: f"user{n}"
    )

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

    # owner را موقع ساخت حتماً می‌دهیم
    owner = None


class WorkspaceMemberFactory(DjangoModelFactory):

    class Meta:
        model = workspace_members

    workspace = None
    user = None
    role = "Mb"


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

    workspace = None
    create_by = None

    status = factory.LazyFunction(
        lambda: random.choice([
            "pn",
            "ac",
            "cp",
        ])
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

    project = None
    assign = None
    create_by = None

    status = factory.LazyFunction(
        lambda: random.choice([
            "td",
            "ip",
            "rw",
            "dn",
        ])
    )

    priority = factory.LazyFunction(
        lambda: random.choice([
            "lw",
            "md",
            "hg",
            "nc",
        ])
    )

    deadline = factory.LazyFunction(
        lambda: timezone.now()
        + timedelta(days=random.randint(1, 30))
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

    name = None


# =========================================================
# CREATE ALL DATA
# =========================================================

@transaction.atomic
def create():

    print("Deleting old data...")

    # -----------------------------------------------------
    # DELETE OLD DATA
    # -----------------------------------------------------

    workspace_members.objects.all().delete()
    tasks.objects.all().delete()
    project.objects.all().delete()
    label.objects.all().delete()
    workspace.objects.all().delete()
    User.objects.all().delete()

    print("Old data deleted.")

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    users = UserFactory.create_batch(30)

    print(f"{len(users)} users created.")

    # -----------------------------------------------------
    # WORKSPACES
    # -----------------------------------------------------

    workspaces = []

    for i in range(8):

        # Owner از همان 30 User انتخاب می‌شود
        owner = random.choice(users)

        ws = WorkspaceFactory(
            name=f"Workspace {i + 1}",
            owner=owner,
        )

        workspaces.append(ws)

    print(
        f"{len(workspaces)} workspaces created."
    )

    # -----------------------------------------------------
    # WORKSPACE MEMBERS
    # -----------------------------------------------------

    for ws in workspaces:

        # =============================================
        # OWNER
        # =============================================

        WorkspaceMemberFactory(
            workspace=ws,
            user=ws.owner,
            role="OW",
        )

        # =============================================
        # OTHER USERS
        # =============================================

        available_users = [
            user
            for user in users
            if user.pk != ws.owner_id
        ]

        member_count = random.randint(
            4,
            min(7, len(available_users))
        )

        selected_users = random.sample(
            available_users,
            member_count
        )

        # دو نفر Admin
        admin_count = min(
            2,
            len(selected_users)
        )

        for user in selected_users[:admin_count]:

            WorkspaceMemberFactory(
                workspace=ws,
                user=user,
                role="AD",
            )

        # بقیه Member
        for user in selected_users[admin_count:]:

            WorkspaceMemberFactory(
                workspace=ws,
                user=user,
                role="Mb",
            )

    print("Workspace members created.")

    # -----------------------------------------------------
    # PROJECTS
    # -----------------------------------------------------

    projects = []

    for ws in workspaces:

        members = list(
            workspace_members.objects
            .filter(workspace=ws)
            .select_related("user")
        )

        member_users = [
            member.user
            for member in members
        ]

        for i in range(4):

            creator = random.choice(
                member_users
            )

            project_obj = ProjectFactory(
                name=f"{ws.name} - Project {i + 1}",
                workspace=ws,
                create_by=creator,
            )

            projects.append(project_obj)

    print(
        f"{len(projects)} projects created."
    )

    # -----------------------------------------------------
    # TASKS
    # -----------------------------------------------------

    tasks_list = []

    for project_obj in projects:

        members = list(
            workspace_members.objects
            .filter(
                workspace=project_obj.workspace
            )
            .select_related("user")
        )

        member_users = [
            member.user
            for member in members
        ]

        for i in range(5):

            assigned_user = random.choice(
                member_users
            )

            creator = random.choice(
                member_users
            )

            task = TaskFactory(
                title=(
                    f"{project_obj.name} "
                    f"- Task {i + 1}"
                ),
                project=project_obj,
                assign=assigned_user,
                create_by=creator,
            )

            tasks_list.append(task)

    print(
        f"{len(tasks_list)} tasks created."
    )

    # -----------------------------------------------------
    # LABELS
    # -----------------------------------------------------

    labels = []

    for label_name in LABEL_CHOICES:

        label_obj = LabelFactory(
            name=label_name
        )

        labels.append(label_obj)

    print(
        f"{len(labels)} labels created."
    )

    # -----------------------------------------------------
    # ASSIGN LABELS
    # -----------------------------------------------------

    shuffled_tasks = tasks_list.copy()

    random.shuffle(
        shuffled_tasks
    )

    # هر Label حداقل به یک Task
    for label_obj, task in zip(
        labels,
        shuffled_tasks
    ):

        label_obj.task_table.add(task)

    # هر Task بین 1 تا 3 Label
    for task in tasks_list:

        selected_labels = random.sample(
            labels,
            random.randint(
                1,
                min(3, len(labels))
            )
        )

        for label_obj in selected_labels:

            label_obj.task_table.add(task)

    # -----------------------------------------------------
    # PRINT RESULT
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("WORKSPACE MEMBERS")
    print("=" * 60)

    for ws in workspaces:

        print(
            f"\n{ws.name}"
            f" | OWNER = {ws.owner.username}"
        )

        members = (
            workspace_members.objects
            .filter(workspace=ws)
            .select_related("user")
        )

        for member in members:

            print(
                f"    {member.user.username}"
                f" -> {member.role}"
            )

    print("\n" + "=" * 60)
    print("Fake data created successfully!")
    print("=" * 60)