AutoGrow
==========

**AutoGrow** :cite:p:`wen_autogrow_2020` considers the problem
of increasing the number of blocks in
ResNet :cite:p:`he_deep_2016` and
VGG :cite:p:`simonyan_very_2015` style architectures, by
organising the network into several “stages”. The first block in each
stage implements a downsampling of the spatial resolution, after which
the spatial resolution is fixed for the remaining blocks in that stage.
By increasing the number of blocks, one can grow the network to an
arbitrary depth while respecting shape constraints. They contest the
[[Net2Net]] notion that function-preserving morphisms are the best way
to
initialise new layer weights, and instead prefer random
initialisation :cite:p:`wen_autogrow_2020`. This has
corroborated by later layer-growing
studies :cite:p:`wu_when_2024`.

