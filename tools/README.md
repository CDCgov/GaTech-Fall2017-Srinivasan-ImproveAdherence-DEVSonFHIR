# Tools to reproduce Docker images

### FHIR server

The FHIR server Docker image is based on the image at
https://hub.docker.com/r/djohnson325/small-fhir/, but with some
modifications to the sample data in order for our project to have
a variety of mock FHIR data for testing and demonstration purposes.
The FHIRUpdate.py python script in this *tools* directory can be
used to recreate the sample data modifications.

This script is only useful when starting from a fresh copy of the
hapi-fhir-jpaserver-example Docker container (either pulled from
https://hub.docker.com/r/djohnson325/small-fhir/ or reproduced from
a DSTU2 version of https://github.com/jamesagnew/hapi-fhir).

**Prerequisites**

The script works with Python 2.7 and the Python SMART on FHIR client,
version 1.0.3 (as it supports the DSTU2 FHIR specification).

Instructions for installing the SMART on FHIR client are available at
https://github.com/smart-on-fhir/client-py.

---

### Sample EHR (CDS Hooks Sandbox) server

The CDS Hooks Sandbox Docker image was created from a modified version
of the official CDS Hooks Sandbox repo at
https://github.com/cds-hooks/sandbox. The purpose of the modifications
was mostly to help users of this project avoid having to manually
enter in patient IDs and configuring server names.

The modifications can be reproduced by using the cdshooks.patch file
in this *tools* directory to patch the master branch of the CDS Hooks
Sandbox repo (modifications originally made on commit
4f20be51150494732f33aa3d15dbeb03969c1540). To apply the patch, run "git
apply cdshooks.patch" after cloning the repo and checking out the
specified branch/revision.
