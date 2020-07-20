class GeometryProfile:
    def __init__(self, centre=(0.0, 0.0)):
        """Abstract GeometryProfile, describing an object with y, x cartesian
        coordinates """
        self.centre = centre

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class SphericalProfile(GeometryProfile):
    def __init__(self, centre=(0.0, 0.0)):
        """ Generic circular profiles class to contain functions shared by light and
        mass profiles.

        Parameters
        ----------
        centre: (float, float)
            The (y,x) coordinates of the origin of the profile.
        """
        super(SphericalProfile, self).__init__(centre)


class EllipticalProfile(SphericalProfile):
    def __init__(self, centre=(0.0, 0.0),             elliptical_comps=(0.0, 0.0)):
        """ Generic elliptical profiles class to contain functions shared by light
        and mass profiles.

        Parameters
        ----------
        centre: (float, float)
            The (y,x) coordinates of the origin of the profiles
        axis_ratio : float
            Ratio of profiles ellipse's minor and major axes (b/a)
        phi : float
            Rotational angle of profiles ellipse counter-clockwise from positive x-axis
        """
        super(EllipticalProfile, self).__init__(centre)
        self.axis_ratio = axis_ratio
        self.phi = phi


class EllipticalLP(EllipticalProfile):
    """Generic class for an elliptical light profiles"""

    def __init__(self, centre=(0.0, 0.0),             elliptical_comps=(0.0, 0.0)):
        """  Abstract class for an elliptical light-profile.

        Parameters
        ----------
        centre: (float, float)
            The (y,x) coordinates of the origin of the profiles
        axis_ratio : float
            Ratio of light profiles ellipse's minor and major axes (b/a)
        phi : float
            Rotational angle of profiles ellipse counter-clockwise from positive x-axis
        """
        super(EllipticalLP, self).__init__(centre, axis_ratio, phi)


class EllipticalGaussian(EllipticalLP):
    def __init__(
        self, centre=(0.0, 0.0),             elliptical_comps=(0.0, 0.0), intensity=0.1, sigma=0.01
    ):
        """ The elliptical Gaussian profile.

        Parameters
        ----------
        centre: (float, float)
            The (y,x) origin of the light profile.
        axis_ratio : float
            Ratio of light profiles ellipse's minor and major axes (b/a).
        phi : float
            Rotation angle of light profile counter-clockwise from positive x-axis.
        intensity : float
            Overall intensity normalisation of the light profiles (electrons per
            second).
        sigma : float
            The full-width half-maximum of the Gaussian.
        """
        super(EllipticalGaussian, self).__init__(centre, axis_ratio, phi)

        self.intensity = intensity
        self.sigma = sigma
