# Change history

## 14-06-2024 (v1.0.4)
- fixed type validation
- added: set default values for checked configs in admin panel (check configs in list, select action "Set selected config rows to default" and press "Go")
- removed default value from list (it's still available on details page)
- added bool flag "is changed"
- Django 3.2 still support as is but not tested all new changes (use Django 4+ if possible)

## 01-05-2024 (v1.0.3)
- added Django <5.1 support
- editor type depending on the config's type instead of config value's type
- added a history of config changes
- new parameter cache TTL in project settings (use `LC_CACHE_TTL = 1    # cache TTL in seconds (default = 1)`)
- added default value in admin panel
- postgres dependency removed (for Django >= 4.0)

## 09-04-2024 (v1.0.2)
- added Django 5 support
- removed dependency django-more-admin-filters
- fixed type validation for multi-type configs
- disabled editor, depending on the value type, for multi-type configs (now it works for one-type configs only)
- updated README

## 16-02-2024 (v1.0.1)
- added Python 3.12 support
- added new example of validator with name decorator
- added editor, depending on the value type
