
Feature: Delete Category
  As a user
  I want to delete unnecessary categories
  So that I can keep my task classifications organized

  Background:
    Given the Todo Manager API is running
    And I have recorded the current category collection

  # Normal Flow
  Scenario Outline: Delete an existing category
    Given I have created a category named "<title>"
    When I delete the category I last created
    Then the response status should be 200
    And the deleted category should no longer be retrievable

    Examples:
      | title       |
      | Old errands |

  # Alternate Flow
  Scenario Outline: Delete one category and keep another
    Given I have created a category named "<kept_title>"
    And I have created a category named "<deleted_title>"
    When I delete the category I last created
    Then the response status should be 200
    And the deleted category should no longer be retrievable
    And the first category I created should still have title "<kept_title>"

    Examples:
      | kept_title | deleted_title |
      | Keep notes | Old notes     |

  # Error Flow
  Scenario Outline: Reject deleting the same category twice
    Given I have created a category named "<title>"
    And the category I last created has been deleted
    When I delete the category I last created
    Then the response status should be 404
    And the category collection should be unchanged

    Examples:
      | title        |
      | Expired list |
