
README
======

Small playground application around the topic of handling todo items on a
shared todo list.

It's based on the backbone.js TODO example application and contains some
experiments around integration with a Django based backend.



Select REST backend endpoint
----------------------------

The application is prepared to be used with multiple REST beackend
implementations to be able to easily switch between examples. The query
parameter `rest_base` can be used to switch the REST endpoint.

* The default piston based backend will be opened if this URL is used:

  http://localhost:8000/

* An empty implementation is prepared to start some manuel experiments:

  http://localhost:8000/?rest_base=/rest-empty/
