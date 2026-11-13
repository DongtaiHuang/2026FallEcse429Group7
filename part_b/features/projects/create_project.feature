
Feature: Create Project
  As a user
  I want to create a new project
  So that I can organize my related tasks

  Background:
    Given the Project API is running

  # Normal Flow
  Scenario Outline: Create a project with title and description
    When I create a project with title "<title>" and description "<description>"
    Then the project response status should be 201
    And the created project should have title "<title>"
    And the created project should have description "<description>"

    Examples:
      | title          | description             |
      | ECSE 429       | Software testing        |
      | Final Project  | Complete course project |

  # Alternate Flow
  Scenario Outline: Create a project with only a title
    When I create a project with only title "<title>"
    Then the project response status should be 201
    And the created project should have title "<title>"

    Examples:
      | title          |
      | Personal Tasks |
      | Winter Studies |

  # Error Flow
  Scenario Outline: Reject a project with invalid completion status
    When I attempt to create a project with title "<title>" and invalid completed value "<completed>"
    Then the project response status should be 400
    And the project collection should remain unchanged

    Examples:
      | title            | completed     |
      | Invalid Project  | not-a-boolean |
      | Incorrect Status | finished      |
