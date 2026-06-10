The Growing Wiki
================

.. figure:: /_static/neuron_addition.svg
   :alt: Neuron addition schematic
   :align: right
   :figclass: home-neuron-figure
   :figwidth: 32%
   :target: overview/neuron_addition_problem.html
   :width: 100%

   Illustration of :doc:`neuron addition <overview/neuron_addition_problem>`
   in a growing network.

Growing Neural Networks start small and grow over the course of training, by e.g. adding neurons or layers. By only growing as large as necessary, and no larger, such methods offer the potential of improved efficiency and remove the need to select architectures by hand.

The Growing Wiki is primarily maintained by the `Inria Tau team <https://www.inria.fr/en/tau>`__, but outside contributors are always welcome on `GitHub <https://github.com/growingnet/growing_wiki>`__. We also manage the `Gromo <https://github.com/growingnet/gromo>`__ PyTorch package for growing neural networks.

..
    Note: This hidden toctree determines which items appear in the sidebar, and must be updated when a new page is added.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents

   overview/index
   applications/non_stationary
   applications/sparse_grow_prune
   applications/transformers
   algorithms/net2net
   algorithms/network_morphism
   algorithms/north
   algorithms/gradmax
   algorithms/splitting
   algorithms/firefly
   algorithms/tiny
   algorithms/senn
   algorithms/autogrow
   algorithms/nest
   algorithms/variance_transfer
   algorithms/fra_grow
   algorithms/sensli

.. container:: home-grid home-grid-rows

   .. container:: home-card

      **Introduction to growing NNs**

      Start here for an introduction and the mathematical background behind growing methods.

      - :doc:`Introduction <overview/index>`
      - :doc:`Neuron addition problem <overview/neuron_addition_problem>`
      - :doc:`Exploiting function geometry <overview/exploiting_function_geometry>`
      - :doc:`Beyond neuron addition <overview/beyond_neuron_addition>`

   .. container:: home-card

      **Growing design questions**

      The problem of growth can be divided into a number of key questions.

      - :doc:`When to grow? <overview/when_to_grow>`
      - :doc:`Where to grow? <overview/where_to_grow>`
      - :doc:`How to grow? <overview/how_to_grow>`
      - :doc:`When to stop? <overview/when_to_stop>`
      - :doc:`Future directions <overview/future>`

   .. container:: home-card

      **Applications**

      A number of concrete applications of Growing Neural Networks.

      - :doc:`Non-stationary data <applications/non_stationary>`
      - :doc:`Sparse growth and grow-prune <applications/sparse_grow_prune>`
      - :doc:`Growing Transformers <applications/transformers>`

Taxonomy of growing algorithms
------------------------------

Growing algorithms can be classified across multiple axes: the type of growth, whether we aim to preserve the function output during growth or improve it, and also the objective that they aim to optimise during growth. We provide a non-exhaustive classification of growth methods.

.. container:: home-grid home-grid-wide home-grid-pills

   .. container:: home-card

      **Growing width**

      Expanding existing layers by adding neurons, or sparse connections.

      - :doc:`Net2Net <algorithms/net2net>`
      - :doc:`Network Morphism <algorithms/network_morphism>`
      - :doc:`NORTH <algorithms/north>`
      - :doc:`GradMax <algorithms/gradmax>`
      - :doc:`Splitting <algorithms/splitting>`
      - :doc:`Firefly <algorithms/firefly>`
      - :doc:`Tiny <algorithms/tiny>`
      - :doc:`SENN <algorithms/senn>`
      - :doc:`NeST <algorithms/nest>`
      - :doc:`Variance Transfer <algorithms/variance_transfer>`

   .. container:: home-card

      **Growing depth**

      Inserting entire layers or blocks to a network.

      - :doc:`Net2Net <algorithms/net2net>`
      - :doc:`Network Morphism <algorithms/network_morphism>`
      - :doc:`AutoGrow <algorithms/autogrow>`
      - :doc:`FRAGrow <algorithms/fra_grow>`
      - :doc:`Firefly <algorithms/firefly>`
      - :doc:`SENN <algorithms/senn>`

   .. container:: home-card

      **Function-preserving morphisms**

      Growth operations that preserve the model's current function output.

      - :doc:`Net2Net <algorithms/net2net>`
      - :doc:`Network Morphism <algorithms/network_morphism>`
      - :doc:`Splitting <algorithms/splitting>`
      - :doc:`GradMax <algorithms/gradmax>`
      - :doc:`NORTH <algorithms/north>`
      - :doc:`Variance Transfer <algorithms/variance_transfer>`
      - :doc:`SENN <algorithms/senn>`

   .. container:: home-card

      **Function-changing/improving morphisms**

      Methods which change or try to improve the function output during growth.

      - :doc:`Tiny <algorithms/tiny>`
      - :doc:`Firefly <algorithms/firefly>`
      - :doc:`NeST <algorithms/nest>`
      - :doc:`FRAGrow <algorithms/fra_grow>`
      - :doc:`AutoGrow <algorithms/autogrow>`

.. container:: project-logo-footer

   .. container:: project-logo-item

      .. container:: project-logo-variant only-light

         .. image:: /_static/logos/inria.png
            :alt: Inria
            :class: logo-inria
            :target: https://www.inria.fr/fr

      .. container:: project-logo-variant only-dark

         .. image:: /_static/logos/inria-inverted.png
            :alt: Inria
            :class: logo-inria
            :target: https://www.inria.fr/fr

   .. container:: project-logo-item

      .. container:: project-logo-variant only-light

         .. image:: /_static/logos/logo_lisn.png
            :alt: LISN
            :class: logo-lisn
            :target: https://www.lisn.upsaclay.fr/

      .. container:: project-logo-variant only-dark

         .. image:: /_static/logos/logo_lisn-inverted.png
            :alt: LISN
            :class: logo-lisn
            :target: https://www.lisn.upsaclay.fr/

   .. container:: project-logo-item

      .. container:: project-logo-variant only-light

         .. image:: /_static/logos/Logo_Universite_Paris-Saclay.png
            :alt: Universite Paris-Saclay
            :class: logo-paris-saclay
            :target: https://www.universite-paris-saclay.fr/

      .. container:: project-logo-variant only-dark

         .. image:: /_static/logos/Logo_Universite_Paris-Saclay-inverted.png
            :alt: Universite Paris-Saclay
            :class: logo-paris-saclay
            :target: https://www.universite-paris-saclay.fr/

   .. container:: project-logo-item

      .. container:: project-logo-variant only-light

         .. image:: /_static/logos/tau.png
            :alt: Tau team
            :class: logo-tau tau-logo
            :target: https://www.inria.fr/en/tau

      .. container:: project-logo-variant only-dark

         .. image:: /_static/logos/tau-inverted.png
            :alt: Tau team
            :class: logo-tau tau-logo
            :target: https://www.inria.fr/en/tau

   .. container:: project-logo-item

      .. container:: project-logo-variant only-light

         .. image:: /_static/logos/logo_manolo.png
            :alt: Manolo project
            :class: logo-manolo
            :target: https://manolo-project.eu/

      .. container:: project-logo-variant only-dark

         .. image:: /_static/logos/logo_manolo-inverted.png
            :alt: Manolo project
            :class: logo-manolo
            :target: https://manolo-project.eu/

   .. container:: project-logo-item

      .. container:: project-logo-variant only-light

         .. image:: /_static/logos/logo_frugal_bg_white.png
            :alt: Gromo
            :class: logo-gromo
            :target: https://github.com/growingnet/gromo

      .. container:: project-logo-variant only-dark

         .. image:: /_static/logos/logo_frugal_bg_white-inverted.png
            :alt: Gromo
            :class: logo-gromo
            :target: https://github.com/growingnet/gromo
