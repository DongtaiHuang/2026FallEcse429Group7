
Feature: View Projects
  As a user
  I want to view my projects
  So that I can manage my ongoing work

  Background:
    Given the Project API is running

  # Normal Flow
  Scenario Outline: View project list with an existing project
    Given a project exists with title "<title>"
    When I request the project list
    Then the project response status should be 200
    And the project list should contain title "<title>"

    Examples:
      | title           |
      | ECSE 429        |
      | Software Design |

  # Alternate Flow
  Scenario Outline: View multiple projects
    Given a project exists with title "<first_title>"
    And another project exists with title "<second_title>"
    When I request the project list
    Then the project response status should be 200
    And the project list should contain title "<first_title>"
    And the project list should contain title "<second_title>"

    Examples:
      | first_title | second_title   |
      | School      | Personal Tasks |
      | Backend     | Frontend       |

  # Error Flow
  Scenario Outline: View a project with an invalid ID
    When I request a project with ID <project_id>
    Then the project response status should be 404
    And no project should be returned

    Examples:
      | project_id |
      | -1         |
      | -999       |
