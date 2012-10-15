

"""
Feature: Start actor servers with different configurations

  Scenario: Start Controller and two real actors and query values
    Given the Actors
        |port| value_range|
        |9001| [1,2]|
        |9002| [1,2]|
    And the Controllers
        |port| actors      |
        |9003| ["http://localhost:9001","http://localhost:9002"] |
    When I query 9001 "/"
    Then I receive status 200
    And I receive json "{'value':1}"
    When I query 9002 "/"
    Then I receive status 200
    And I receive json "{'value':1}"
    When I query 9003 "/"
    Then I receive status 200
    And I receive json "{'value':2}"


  Scenario: Start Controller and two real actors and set maximum value
    Given the Actors
        |port| value_range|
        |9001| [1,2]|
        |9002| [1,2]|
    And the Controllers
        |port| actors      |
        |9003| ["http://localhost:9001","http://localhost:9002"] |
    When I update 9003 "/" with "3"
    Then I receive status 200
    And I receive json "{'value':3}"
    And actor 9001 value is "{'value':2}"
    And actor 9002 value is "{'value':1}"


  Scenario: Start Controller and two real actors and set new value
    Given the Actors
        |port| value_range|
        |9001| [1,2]|
        |9002| [1,2]|
    And the Controllers
        |port| actors      |
        |9003| ["http://localhost:9001","http://localhost:9002"] |
    When I update 9003 "/" with "0"
    Then I receive status 400
    And I receive content "Input error: 0 is not an satisfiable"
    And actor 9001 value is "{'value':1}"
    And actor 9002 value is "{'value':1}"


  Scenario: Start Controller and two real actors and deny to set value
    Given the Actors
        |port| value_range|
        |9001| [1,2]|
        |9002| [1,2]|
    And the Controllers
        |port| actors      |
        |9003| ["http://localhost:9001","http://localhost:9002"] |
    When I update 9003 "/" with "Null"
    Then I receive status 400
    And I receive content "Input error: Not a valid integer: 'Null'"
    And actor 9001 value is "{'value':1}"
    And actor 9002 value is "{'value':1}"


  Scenario: Start Controller and two real actors and set value multiple time
    Given the Actors
        |port| value_range|
        |9001| [1,2]|
        |9002| [1,2]|
    And the Controllers
        |port| actors      |
        |9003| ["http://localhost:9001","http://localhost:9002"] |
    When I update 9003 "/" with "3"
    Then I receive status 200
    And I receive json "{'value':3}"
    And actor 9001 value is "{'value':2}"
    And actor 9002 value is "{'value':1}"
    When I update 9003 "/" with "2"
    Then I receive status 200
    And I receive json "{'value':2}"
    And actor 9001 value is "{'value':1}"
    And actor 9002 value is "{'value':1}"
    When I update 9003 "/" with "4"
    Then I receive status 200
    And I receive json "{'value':4}"
    And actor 9001 value is "{'value':2}"
    And actor 9002 value is "{'value':2}"


  Scenario: Start Controller of two Controllers and two real actors return values
    Given the Actors
        |port| value_range|
        |9001| [1,2]|
        |9002| [1,2]|
        |9003| [1,2]|
        |9004| [1,2]|
    And the Controllers
        |port| actors      |
        |9005| ["http://localhost:9001","http://localhost:9002"] |
        |9006| ["http://localhost:9003","http://localhost:9004"] |
        |9007| ["http://localhost:9005","http://localhost:9006"] |

    When I query 9001 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

    When I query 9002 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

    When I query 9003 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

    When I query 9004 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

    When I query 9005 "/"
    Then I receive status 200
    And I receive json "{'value':2}"

    When I query 9006 "/"
    Then I receive status 200
    And I receive json "{'value':2}"

    When I query 9007 "/"
    Then I receive status 200
    And I receive json "{'value':4}"


  Scenario: Start Controller of two Controllers and two real actors and set value
    Given the Actors
        |port| value_range|
        |9001| [1,2]|
        |9002| [1,2]|
        |9003| [1,2]|
        |9004| [1,2]|
    And the Controllers
        |port| actors      |
        |9005| ["http://localhost:9001","http://localhost:9002"] |
        |9006| ["http://localhost:9003","http://localhost:9004"] |
        |9007| ["http://localhost:9005","http://localhost:9006"] |

    When I update 9007 "/" with "8"
    Then I receive status 200
    And I receive json "{'value':8}"

    When I query 9001 "/"
    Then I receive status 200
    And I receive json "{'value':2}"

    When I query 9002 "/"
    Then I receive status 200
    And I receive json "{'value':2}"

    When I query 9003 "/"
    Then I receive status 200
    And I receive json "{'value':2}"

    When I query 9004 "/"
    Then I receive status 200
    And I receive json "{'value':2}"

    When I query 9005 "/"
    Then I receive status 200
    And I receive json "{'value':4}"

    When I query 9006 "/"
    Then I receive status 200
    And I receive json "{'value':4}"

    When I query 9007 "/"
    Then I receive status 200
    And I receive json "{'value':8}"


  Scenario: Start Controller of two Controllers and two real actors and deny to set value
    Given the Actors
        |port| value_range|
        |9001| [1,2]|
        |9002| [1,2]|
        |9003| [1,2]|
        |9004| [1,2]|
    And the Controllers
        |port| actors      |
        |9005| ["http://localhost:9001","http://localhost:9002"] |
        |9006| ["http://localhost:9003","http://localhost:9004"] |
        |9007| ["http://localhost:9005","http://localhost:9006"] |

    When I update 9007 "/" with "9"
    Then I receive status 400
    And I receive content "Input error: 9 is not an satisfiable"

    When I query 9001 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

    When I query 9002 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

    When I query 9003 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

    When I query 9004 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

    When I query 9005 "/"
    Then I receive status 200
    And I receive json "{'value':2}"

    When I query 9006 "/"
    Then I receive status 200
    And I receive json "{'value':2}"

    When I query 9007 "/"
    Then I receive status 200
    And I receive json "{'value':4}"


"""
