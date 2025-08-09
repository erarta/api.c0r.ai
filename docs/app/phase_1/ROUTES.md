# Routes and Navigation

## Route names
- /onboarding/intro
- /onboarding/gender
- /onboarding/activity
- /onboarding/weight
- /onboarding/age
- /onboarding/goal
- /onboarding/desired-weight
- /onboarding/questions
- /onboarding/summary
- /home
- /home/analysis/result
- /progress
- /progress/weight/update
- /progress/goals
- /progress/settings
- /progress/refer-friend
- /settings
- /settings/language
- /settings/delete-account
- /extras/entries/multi-add
- /extras/food-db

## Graph
- Auth+Onboarding stack → Main tabs (Home, Progress, Settings)
- Home contains capture and analysis result flows with modals/sheets
- Progress contains subflows (weight update, goals, settings)

## Deep links (placeholders)
- c0r://home
- c0r://analyze?source=camera
- c0r://progress?range=30
- c0r://settings/language

## Navigation notes
- Use typed routes; central RouteRegistry for testability
- Preserve state on tab switch; lazy load tab content
- Handle back behavior per platform (Android back → tab back, iOS swipe back)
