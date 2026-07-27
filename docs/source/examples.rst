Examples
========

RDKit Calculator tutorial
-------------------------

``examples/example.ipynb`` covers:

* environment notes (Java, RDKit, ``padelpy2[calc]``)
* a minimal ``Calculator([Weight])`` example
* stock-JAR aromatic counts vs ``detectaromaticity=True``
* a small custom descriptor subset (ALOGP / Crippen / Weight)

https://github.com/Cognitive-Chemistry-Labs/padelpy2/blob/main/examples/example.ipynb

Low-level ``padeldescriptor`` (no RDKit / pandas)
-------------------------------------------------

``examples/padeldescriptor_lowlevel.ipynb`` assumes a **minimal** install
(``pip install padelpy2`` only): Java on ``PATH``, file-based
``padeldescriptor``, and stdlib CSV reading. It does **not** import RDKit or
pandas, and uses ``from padelpy2.wrapper import padeldescriptor`` so the
Calculator stack is never loaded.

https://github.com/Cognitive-Chemistry-Labs/padelpy2/blob/main/examples/padeldescriptor_lowlevel.ipynb

Open from a checkout::

   jupyter notebook examples/example.ipynb
   jupyter notebook examples/padeldescriptor_lowlevel.ipynb

Related pages: :doc:`installation`, :doc:`quickstart`, :doc:`when_to_use`,
:doc:`migration`.
