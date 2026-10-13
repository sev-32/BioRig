"""R584 supported-contact no-slip correction for LUCID's native MuJoCo plant.

One solver parameter only. Does not change R574/R582, geometry, contact
coefficients, muscles, initial physics, or externally apply root constraints.
"""
from __future__ import annotations
import hashlib
import numpy as np


def material_digest(model):
    """Fingerprint of material, physical geometry and body mass arrays."""
    arrays=(model.geom_friction,model.geom_solref,model.geom_solimp,
            model.geom_size,model.body_mass)
    return hashlib.sha256(np.concatenate([np.asarray(a).ravel() for a in arrays]).tobytes()).hexdigest()


def configure(model, iterations=6, tolerance=1e-6):
    """Enable the additional MuJoCo tangential no-slip solver on this clone.

    Baseline R574 remains frozen. This affects only the passed MjModel instance.
    The solver remains Coulomb-friction constrained and may legitimately slip if
    the support forces exceed its physical cone or contacts are absent.
    """
    if not isinstance(iterations,int) or not (0 <= iterations <= 20):
        raise ValueError('no-slip iterations must be an integer between 0 and 20')
    if not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError('no-slip tolerance must be positive and finite')
    before=material_digest(model)
    model.opt.noslip_iterations=iterations
    model.opt.noslip_tolerance=float(tolerance)
    if material_digest(model)!=before:
        raise AssertionError('R584 may not change material/geometry/mass settings')
    return {'noSlipIterations':iterations,'noSlipTolerance':float(tolerance),
            'materialAndMassSHA256':before}
