# Tracker App Unit Tests

This directory contains comprehensive unit tests for the Tracker app following Django and Python best practices.

## 📁 Test Structure

```
tracker/tests/
├── __init__.py              # Test package initialization
├── test_models.py           # Model tests (entities, relationships, properties)
├── test_forms.py            # Form tests (validation, clean methods)
├── test_views.py            # View tests (HTTP responses, context, templates)
├── test_api.py              # REST API tests (ViewSet, serializers via API)
├── test_serializers.py      # Serializer tests (DRF serializers)
├── test_signals.py          # Signal tests (post_save handlers)
├── test_tasks.py            # Celery task tests
└── README.md                # This file
```

## 🎯 Test Coverage

### 1. **test_models.py** - Model Tests

Tests all model functionality including:

- ✅ Model creation and instance validation
- ✅ String representations (`__str__` methods)
- ✅ Model properties (`display_label`, `submission_expiry`, etc.)
- ✅ Model relationships (ForeignKey, ManyToMany)
- ✅ Unique constraints and validation
- ✅ Custom model methods (`get_status_display`, `get_transferred_opportunity`)
- ✅ File upload paths
- ✅ Default ordering

**Models tested:**

- FundingAgency
- Client
- Institute
- Unit
- Staff
- Country
- Currency
- Opportunity
- OpportunityFile

### 2. **test_forms.py** - Form Tests

Tests all form validation and behavior:

- ✅ Form field validation
- ✅ Custom `clean()` methods
- ✅ Required field enforcement
- ✅ Conditional validation (e.g., currency required when amount is provided)
- ✅ Custom widgets and attributes
- ✅ Form initialization and context
- ✅ Error messages

**Forms tested:**

- LoginForm
- OpportunityForm
- UpdateOpportunityForm
- UpdateStatusForm
- SubmitProposalForm
- OpportunitySearchForm
- FundingAgencyForm
- ClientForm
- Custom choice fields (FundingAgencyChoiceField, ClientChoiceField)

### 3. **test_views.py** - View Tests

Tests all view functionality:

- ✅ HTTP methods (GET, POST, PUT, DELETE)
- ✅ Authentication and authorization
- ✅ Template rendering
- ✅ Context data
- ✅ Form handling in views
- ✅ Redirects and success URLs
- ✅ HTMX-specific behavior
- ✅ Pagination
- ✅ Filtering and search
- ✅ File uploads
- ✅ Transfer functionality (EOI to RFP)

**Views tested:**

- IndexView
- OpportunityListView (with pagination and filtering)
- OpportunityCreateView (including file uploads and transfers)
- OpportunityUpdateView
- OpportunityStatusUpdateView
- OpportunitySubmitView
- OpportunityDetailView (including AJAX)
- OpportunityDetailAnonymousView
- FileDeleteView
- NewFundingAgencyView
- NewClientView
- TransferOpportunityView

### 4. **test_api.py** - REST API Tests

Tests the REST API endpoints:

- ✅ JWT authentication
- ✅ CRUD operations via API
- ✅ List/retrieve/create/update/delete
- ✅ Permission checks
- ✅ Response format validation
- ✅ Read-only fields enforcement
- ✅ Related field handling
- ✅ Validation errors

**API tested:**

- OpportunityViewSet (all CRUD operations)
- Authentication and permissions
- Token-based access control

### 5. **test_serializers.py** - Serializer Tests

Tests DRF serializers:

- ✅ Field serialization
- ✅ Read-only fields
- ✅ Create/update operations
- ✅ Validation
- ✅ Relationship handling

### 6. **test_signals.py** - Signal Tests

Tests Django signals:

- ✅ Post-save signal triggers
- ✅ Create vs update differentiation
- ✅ Notification dispatch
- ✅ Celery task triggering

### 7. **test_tasks.py** - Celery Task Tests

Tests asynchronous tasks:

- ✅ Task execution
- ✅ Task logic
- ✅ Date filtering
- ✅ Notification sending
- ✅ Edge cases (no data, no subscriptions)

## 🚀 Running the Tests

### Run All Tracker Tests

```bash
python manage.py test tracker
```

### Run Specific Test Module

```bash
python manage.py test tracker.tests.test_models
python manage.py test tracker.tests.test_forms
python manage.py test tracker.tests.test_views
python manage.py test tracker.tests.test_api
python manage.py test tracker.tests.test_serializers
python manage.py test tracker.tests.test_signals
python manage.py test tracker.tests.test_tasks
```

### Run Specific Test Class

```bash
python manage.py test tracker.tests.test_models.OpportunityModelTest
python manage.py test tracker.tests.test_forms.OpportunityFormTest
```

### Run Specific Test Method

```bash
python manage.py test tracker.tests.test_models.OpportunityModelTest.test_opportunity_creation
```

### Run with Verbosity

```bash
# More detailed output
python manage.py test tracker --verbosity=2

# Even more detailed (shows each test)
python manage.py test tracker --verbosity=3
```

### Run with Coverage

```bash
# Install coverage first
pip install coverage

# Run tests with coverage
coverage run --source='tracker' manage.py test tracker

# View coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

### Run Tests in Parallel (faster)

```bash
python manage.py test tracker --parallel
```

### Keep Test Database

```bash
# Useful for debugging
python manage.py test tracker --keepdb
```

## 📊 Test Best Practices Applied

### 1. **Arrange-Act-Assert (AAA) Pattern**

Each test follows the clear structure:

```python
def test_example(self):
    # Arrange: Set up test data
    user = User.objects.create(...)

    # Act: Perform the action
    opportunity = Opportunity.objects.create(...)

    # Assert: Verify the result
    self.assertEqual(opportunity.created_by, user)
```

### 2. **setUp and tearDown Methods**

- Common test data created in `setUp()` to avoid repetition
- Resources cleaned up in `tearDown()` when needed
- Each test is isolated and independent

### 3. **Descriptive Test Names**

- Test names clearly describe what is being tested
- Format: `test_<what>_<condition>_<expected_result>`
- Examples:
  - `test_opportunity_form_missing_title`
  - `test_list_opportunities_requires_authentication`
  - `test_status_update_to_go`

### 4. **Comprehensive Docstrings**

Every test class and method has clear documentation explaining purpose and behavior.

### 5. **Mocking External Dependencies**

- External services (Celery tasks, notifications) are mocked
- Tests remain fast and don't depend on external systems
- Uses `@patch` decorator for mocking

### 6. **Test Isolation**

- Each test can run independently
- No dependencies between tests
- Database is reset between tests

### 7. **Edge Cases Covered**

- Missing required fields
- Invalid data
- Boundary conditions
- Empty results
- Null values
- Permission checks

### 8. **Settings Override**

Tests use `@override_settings` when needed:

```python
@override_settings(MEDIA_ROOT='/tmp/test_media/')
def test_file_upload(self):
    ...
```

## 🔧 Test Database

Django automatically creates a test database for running tests:

- Prefix: `test_`
- Example: `test_opportunity_tracker`
- Automatically created and destroyed
- Migrations are applied
- Completely isolated from production/development data

## 📝 Writing New Tests

When adding new functionality to the tracker app:

1. **Identify what to test:**

   - New models? Add to `test_models.py`
   - New forms? Add to `test_forms.py`
   - New views? Add to `test_views.py`
   - New API endpoints? Add to `test_api.py`

2. **Follow the existing pattern:**

   ```python
   class NewFeatureTest(TestCase):
       """Test cases for new feature."""

       def setUp(self):
           """Set up test data."""
           # Create common test data

       def test_feature_works(self):
           """Test that feature works as expected."""
           # Arrange
           # Act
           # Assert
   ```

3. **Run tests frequently:**
   - Run tests before committing
   - Run tests after making changes
   - Ensure all tests pass

## 🎓 Key Testing Concepts

### TestCase vs TransactionTestCase

- **TestCase**: Faster, uses database transactions (used in most tests)
- **TransactionTestCase**: Slower, flushes database (use for testing transactions)

### Client vs APIClient

- **Client**: Django test client for views
- **APIClient**: DRF test client for API endpoints

### Assertions Used

- `assertEqual(a, b)` - Check equality
- `assertTrue(x)` - Check boolean
- `assertFalse(x)` - Check boolean false
- `assertIn(item, container)` - Check membership
- `assertIsNone(x)` - Check None
- `assertIsInstance(obj, cls)` - Check type
- `assertRaises(Exception)` - Check exception raised
- `assertFormError(response, form, field, errors)` - Check form errors
- `assertTemplateUsed(response, template)` - Check template

## 🐛 Debugging Tests

### Run Specific Failing Test

```bash
python manage.py test tracker.tests.test_models.OpportunityModelTest.test_opportunity_creation -v 2
```

### Use pdb for Debugging

Add breakpoint in test:

```python
def test_something(self):
    import pdb; pdb.set_trace()
    # Test code
```

### Print Debug Information

```python
def test_something(self):
    print(f"Opportunity: {opportunity}")
    print(f"Status: {opportunity.status}")
```

## 📈 Test Metrics

Current test statistics:

- **Total test files:** 7
- **Total test classes:** ~30
- **Total test methods:** ~150+
- **Code coverage target:** >80%

## 🤝 Contributing

When contributing tests:

1. Follow existing naming conventions
2. Add docstrings to all test methods
3. Keep tests simple and focused
4. Test both success and failure cases
5. Mock external dependencies
6. Ensure tests are fast (<1 second each)

## 📚 Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

**Last Updated:** November 2024
**Maintained by:** Development Team
