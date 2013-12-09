====
TODO
====

* Complete and polish documenation

Tests to Finish/Perform
=======================
* Set up simulatentous RF runs on full and subdomain once the single run is
  satisfcatory
* Try a subdomain entirely encased in the inlet fulldomain
* Try a setup with a much larger mesh
* Try a larger subdomain within the inlet fulldomain
* Experiment with different forcing frequencies

General Things to Check
=======================
* Max Agnew and Seizo Tanaka's subdomain code
* Think about potential issues where ``fort.13`` changes occur on the boundary
  of a subdomain. I think this is fine, but think about it nonetheless.
* Look into subduration modeling (via HOTSTARTs?)
* Check out they implement the BC for both ETA, U, and V

Updates to Incorporate
======================
* mesh_mapping pacakage that accomodates/is-agnostic to parallel v.s.
  serial version of :program:`Griddtata`
* When doing comparision set a lower threshold for errors and calcualte the
  number of nodes with errors above this threshold (start at 0.15 m)
* Add plotting all error (2D), highlighting threshold errors
* Try looking for a combo of threshold absolute error and relative error
* Add reading of comparision data from ``*.mat`` file
* Add reporting of % of nodes with differences, and with differences over a
  certain threshold

Potential User Bases to Reach out to
====================================
* Max Agnew - Army Corps of Engineers
* John Baugh, Alper Altunas, Jason Simon, Casey Diedtrich - NCSU
* Johannes Westerink - Notre Dame

