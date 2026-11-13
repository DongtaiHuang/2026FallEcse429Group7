
Feature: Link Todo to Project
  As a user
  I want to assign a todo to a project
  So that I can organize related tasks

  Background:
    Given the Interoperability API is running

  # Normal Flow
  Scenario Outline: Link an existing todo to a project
    Given a project named "<project_title>" exists
    And a todo named "<todo_title>" exists
    When I link the todo to the project
    Then the interoperability response status should be 201
    And the project should contain the linked todo
    And the todo should belong to the project

    Examples:
      | project_title | todo_title       |
      | ECSE 429      | Write test cases |
      | Website       | Design homepage  |

  # Alternate Flow
  Scenario Outline: Link a project through the todo endpoint
    Given a project named "<project_title>" exists
    And a todo named "<todo_title>" exists
    When I link the project through the todo endpoint
    Then the interoperability response status should be 201
    And the project should contain the linked todo
    And the todo should belong to the project

    Examples:
      | project_title | todo_title       |
      | Research      | Read papers      |
      | Final Report  | Prepare diagrams |

  # Error Flow
  Scenario Outline: Reject linking an unknown todo
    Given a project named "<project_title>" exists
    When I try to link a todo with invalid ID "<invalid_id>"
    Then the interoperability response status should be 404
    And the project should have no linked todos

    Examples:
      | project_title | invalid_id |
      | Coursework    | abc        |
      | Sprint Tasks  | missing    |
