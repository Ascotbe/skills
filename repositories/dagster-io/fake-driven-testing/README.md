# Fake-Driven Testing

Fake-driven testing is a pragmatic, framework-free approach to testability for codebases built with agents.

## Historical Context

In testing circles, historically there has been much discussion around different approaches to testing: pure unit tests, mocks, stubs, fakes. [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) is a frequently cited article about this topic.

## The Problem: Mock Tautology

Agents writing Python, without constraints, typically create test cases using mocks. When this goes too far, these tests have little value. We call this "mock tautology" or "mock slop" for short.

*A test that mocks out all the real behavior and then asserts the mocks were called — so it's just restating the implementation as assertions. It can never fail unless the code is refactored, and it can never catch a real bug because the mocks don't enforce real semantics. The test is true by construction.*

These tests are worse than harmless and provide a false sense of security.

Here is an example of such a test:

```python
class TestCommitAndPushToMain:
    @patch("repository_operations._stage_all_changes")
    @patch("repository_operations._create_commit")
    @patch("repository_operations._get_default_branch_name")
    @patch("repository_operations._push_branch")
    def test_commit_and_push_to_main_with_main_branch(
        self,
        mock_push,
        mock_get_branch,
        mock_commit,
        mock_stage,
        mock_github_config,
    ):
        repo_path = Path("/tmp/repo")
        title = "Test commit"
        commit_hash = "abc123def456"

        mock_commit.return_value = commit_hash
        mock_get_branch.return_value = "main"

        result = commit_and_push_to_main(
            repo_path,
            title,
            github_config=mock_github_config,
            author_name="testuser",
            author_email="testuser@example.com",
        )

        assert result == commit_hash
        mock_stage.assert_called_once_with(repo_path)
        mock_commit.assert_called_once_with(repo_path, title, "testuser", "testuser@example.com")
        mock_get_branch.assert_called_once_with(repo_path)
        mock_push.assert_called_once_with(repo_path, "main", github_config=mock_github_config)
```

## Dependency Injection Doesn't Fix It

Dependency injection is a common approach to achieve testability. However, when dependency injection is done at *every* layer of the stack it ends up with a number of problems.

* Startup time for simple operations in large applications can be surprisingly slow, as you are forced to eagerly construct large numbers of objects in order to do *anything*.
* Constructing arbitrary objects can be very inconvenient as one needs to construct all the dependencies transitively. You are left to use heavyweight abstractions such as IoC containers in order to do something simple like constructing an object for use in a script.
* For lack of a better term, these codebases end up awkward and weird. There is excessive indirection. There are zombie nouns like "Sender" and "Logger" that could be just verbs that increase cognitive load. There is unnecessary object-orientation at every layer of the stack.

And when you have paid the price of adopting DI, and write the hermetically sealed, fast tests it promises, you are often left with the same problem as the DI-free codebase: mock tautology. You are just writing the implementation twice:

```python
class NotificationService:
    """The thing we're 'testing'."""
    def __init__(
        self,
        email_sender: EmailSender,
        user_repo: UserRepository,
        audit_logger: AuditLogger,
    ):
        self.email_sender = email_sender
        self.user_repo = user_repo
        self.audit_logger = audit_logger

    def notify_user(self, user_id: str, message: str) -> bool:
        email = self.user_repo.get_email(user_id)
        result = self.email_sender.send(email, "Notification", message)
        self.audit_logger.log("notification_sent", {"user_id": user_id, "success": result})
        return result


def test_notify_user():
    # Arrange: inject mocks through constructor
    sender = Mock(spec=EmailSender)
    repo = Mock(spec=UserRepository)
    logger = Mock(spec=AuditLogger)

    repo.get_email.return_value = "alice@test.com"
    sender.send.return_value = True

    service = NotificationService(sender, repo, logger)

    # Act
    result = service.notify_user("user-1", "Hello!")

    # Assert: line-by-line restatement of the implementation
    assert result is True
    repo.get_email.assert_called_once_with("user-1")
    sender.send.assert_called_once_with("alice@test.com", "Notification", "Hello!")
    logger.log.assert_called_once_with("notification_sent", {"user_id": "user-1", "success": True})
```


The use of *fakes* instead of *mocks* can improve this situation, as you can set up state and test more complex scenarios. However, historically they have been too difficult and costly to maintain manually. You have to keep an in-memory implementation up-to-date with the "real" implementation of the class. It is a lot of work to do so, and it is easy to introduce bugs in the testing infrastructure that cause subtle behavior differences between the two, causing both false positives and false negatives, often in subtle, difficult-to-detect ways.

The maintenance costs are specific and compounding. Every time a gateway interface changes — a new parameter, a renamed method, a different return type — *every* implementation must be updated in lockstep: the real one, the fake one, and all the tests that depend on either. The fake must also preserve realistic semantics: if the real database enforces uniqueness constraints, the fake must too, or your scenario tests are testing a world that doesn't exist. And the only way to know the fake has drifted from reality is to write fidelity tests (covered below), which are themselves another artifact to maintain. Historically, this work scaled linearly with the number of gateways and the rate of interface change, which is why most teams gave up and reached for mocks.

AI agents collapse this cost. An agent building a feature that changes a gateway interface can update the fake in the same pass. An agent can generate and maintain fidelity tests as a byproduct of building the real implementation. And when fidelity tests fail, an agent can diagnose the drift and fix the fake — a task that is mechanical and well-scoped, exactly the kind of work agents excel at. The economics flip: fakes go from "theoretically superior but practically unaffordable" to "the default choice."

This is one case where AI-native engineering enables a fundamentally different tradeoff than was possible historically, because agents can maintain fakes, keep them in sync, and verify their fidelity at relatively low cost.

## The Agentic Solution: Fake-Driven Testing

The core idea:

* Use the [*Gateway*](https://martinfowler.com/articles/gateway-pattern.html) pattern to model interactions with external state and systems that are difficult or slow to test: CLIs, external services, databases, and so forth.
* Have agents maintain *fakes* of these gateways as you build the application.
* Maintain integration tests and ensure fidelity between real and fake implementations of these gateways.
* Write fast, end-to-end tests of scenarios in your application over these fakes.

This is meant to be a pragmatic middle ground. You have a *single* layer of dependency injection at the lowest level possible in the stack. All of these dependencies are typically encapsulated by a single context object. For tests, you can pass in fake versions of these dependencies. You can explicitly set up the state for a user scenario, run it against the fake, and assert against the expected state.

### The Gateway Pattern

A [Gateway](https://martinfowler.com/articles/gateway-pattern.html) is a thin interface over an external system. It owns the I/O boundary and nothing else. Little to no business logic lives here.

```python
# Examples
class EmailGateway(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool: ...
    @abstractmethod
    def get_sent_messages(self) -> list[dict]: ...

class UserGateway(ABC):
    @abstractmethod
    def get_email(self, user_id: str) -> str | None: ...
    @abstractmethod
    def add_user(self, user_id: str, email: str) -> None: ...

class AuditGateway(ABC):
    @abstractmethod
    def log(self, event_name: str, payload: dict) -> None: ...
```

### Real Implementations

The real implementations are thin wrappers. They do I/O, nothing more.

```python
class SmtpEmailGateway(EmailGateway):
    def __init__(self, smtp_host: str, smtp_port: int):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send(self, to: str, subject: str, body: str) -> bool:
        # actual SMTP call
        ...

    def get_sent_messages(self) -> list[dict]:
        # query delivery log from provider
        ...
```

### Fake Implementations

Fakes are in-memory implementations with real semantics. They're not mocks — they maintain state and enforce constraints. They are maintained by agents.

```python
class FakeEmailGateway(EmailGateway):
    def __init__(self):
        self._sent: list[dict] = []
        self._should_fail: set[str] = set()

    def send(self, to: str, subject: str, body: str) -> bool:
        if to in self._should_fail:
            return False
        self._sent.append({"to": to, "subject": subject, "body": body})
        return True

    def get_sent_messages(self) -> list[dict]:
        return list(self._sent)

    # Test-only: scenario setup for error paths
    def set_failure_for(self, email: str) -> None:
        self._should_fail.add(email)
```

Fakes can expose test-only methods (`set_failure_for`) for scenario setup that aren't on the ABC. This is, for example, how you test error paths without contorting the production interface.

### The Context Object

One object, one layer of indirection. This is not a DI container — it's a plain dataclass.

```python
@dataclass(frozen=True)
class AppContext:
    email: EmailGateway
    users: UserGateway
    audit: AuditGateway


def create_production_context(config: AppConfig) -> AppContext:
    return AppContext(
        email=SmtpEmailGateway(config.smtp_host, config.smtp_port),
        users=PostgresUserGateway(config.db_url),
        audit=CloudWatchAuditGateway(config.aws_region),
    )
```

### Business Logic Takes the Context

The business logic is a plain function. No class, no constructor injection, no framework.

```python
def notify_user(ctx: AppContext, user_id: str, message: str) -> bool:
    email = ctx.users.get_email(user_id)
    if email is None:
        ctx.audit.log("notification_failed", {"user_id": user_id, "reason": "no_email"})
        return False

    result = ctx.email.send(email, "Notification", message)
    ctx.audit.log("notification_sent", {"user_id": user_id, "success": result})
    return result
```

### Where DI Stops

The README advocates "a single layer of dependency injection at the lowest level possible." In practice, this means gateways are the *only* DI seam. They are the only place you swap a real implementation for a fake.

Higher-level code that composes multiple gateways — call them services, backends, workflows, whatever fits your domain — is *never* faked. You test the real logic by injecting fake gateways underneath it:

```python
class OnboardingService:
    def __init__(self, ctx: AppContext):
        self.ctx = ctx

    def onboard_user(self, user_id: str, email: str, welcome_message: str) -> bool:
        self.ctx.users.add_user(user_id, email)
        sent = self.ctx.email.send(email, "Welcome!", welcome_message)
        self.ctx.audit.log("user_onboarded", {"user_id": user_id, "email_sent": sent})
        return sent


def test_onboard_user():
    ctx = create_test_context()

    service = OnboardingService(ctx)
    result = service.onboard_user("user-1", "alice@test.com", "Welcome aboard!")

    assert result is True
    assert ctx.users.get_email("user-1") == "alice@test.com"
    assert ctx.email.get_sent_messages() == [
        {"to": "alice@test.com", "subject": "Welcome!", "body": "Welcome aboard!"}
    ]
```

There is no `FakeOnboardingService`. The real `OnboardingService` runs with real logic; only the gateways beneath it are fakes. This is the architectural guardrail that prevents sliding into the over-engineered DI style critiqued earlier — you get testability without an explosion of test doubles at every layer.

### Scenario Tests

For tests, `create_test_context` takes a dictionary describing the initial state of the world. Setup is declarative — no imperative mock wiring.

```python
def test_notify_user():
    ctx = create_test_context({
        "users": [{"id": "user-1", "email": "alice@test.com"}],
    })

    result = notify_user(ctx, "user-1", "Hello!")

    assert result is True
    assert ctx.email.get_sent_messages() == [
        {"to": "alice@test.com", "subject": "Notification", "body": "Hello!"}
    ]
```

Compare this to the mock-tautology version. This test doesn't restate the implementation — it describes a scenario. "A user exists and we notify them." If you refactor `notify_user` — add retry logic, batch audit logs, change the internal call order — this test doesn't break unless the externally visible behavior changes.

This simple example illustrates the point, but it is in more complex scenarios where this approach truly shines. You can setup state to model real-world scenarios and run many tests of them, and do so quickly.

### Fidelity Testing

How do you know the fakes behave like the real implementations? Fidelity tests run the same operations against both and assert the same outcomes.

```python
class GatewayFidelityTest:
    @pytest.fixture(params=["real", "fake"])
    def user_gateway(self, request, test_db_url) -> UserGateway:
        if request.param == "real":
            gw = PostgresUserGateway(test_db_url)
            yield gw
            gw.cleanup()
        else:
            yield FakeUserGateway()

    def test_get_email_returns_none_for_missing_user(self, user_gateway):
        assert user_gateway.get_email("nonexistent") is None

    def test_add_and_retrieve_user(self, user_gateway):
        user_gateway.add_user("user-1", "alice@test.com")
        assert user_gateway.get_email("user-1") == "alice@test.com"
```

These are your slow tests — they hit the real database, the real SMTP server. You run them in CI, not on every keystroke. But they give you confidence that your fast scenario tests are testing real behavior.

### Defense in Depth

The test types introduced above aren't three random categories — they're layers of a defense-in-depth strategy, each protecting against a different class of failure:

- **Fidelity tests** protect the integrity of the fakes themselves. They verify that `FakeUserGateway` behaves like `PostgresUserGateway` so you can trust the foundation your other tests are built on. These are slow (they hit real systems) and run in CI.
- **Scenario tests** protect business logic. They run fast over fakes, cover the combinatorial space of user workflows, and form the bulk of your test suite. Because fidelity tests guard the fakes, you can trust these results.
- **Smoke tests** protect against real-world integration surprises that fakes can't simulate — network timeouts, authentication edge cases, provider API changes, configuration drift between environments. A small suite of end-to-end smoke tests against real systems catches the things no fake can anticipate.

If any layer fails, the ones below it still hold. A fidelity test failure tells you to fix the fake before trusting scenario results. A scenario test failure points to a business logic bug without requiring a slow integration run. A smoke test failure catches environmental issues that no amount of in-process testing can surface. Each layer makes the others more valuable.

## Why This Matters for Agentic Engineering

This means you can test complex scenarios quickly, as there is little to no I/O. The tests are side-effect-free (if gateways are used universally) so they are embarrassingly parallel at the thread, process, and node level.

This is ideal for agentic engineering, where agents thrive on high quality, fast tests. 

Refactoring is a joy. With mock tautology, refactoring is often extremely painful, as all the tests that are just reimplementations of the logic *also* have to be refactored, which is a waste of time, energy, and tokens.

Instead you can refactor and if all fast scenario tests pass you can be confident that the refactoring worked. It directly mirrors the very definition of refactoring: you restructured code with the intent of not changing externally visible behavior.
