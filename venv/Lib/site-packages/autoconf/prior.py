from autoconf.ancestor import AncestorConfig


class DefaultPriorConfig(AncestorConfig):
    """Parses prior config"""

    def get(self, module_name, class_name, attribute_name):
        """

        Parameters
        ----------
        module_name: String
            The analysis_path of the module
        class_name: String
            The analysis_path of the class
        attribute_name: String
            The analysis_path of the attribute

        Returns
        -------
        prior_array: []
            An arrays describing a prior
        """
        arr = (
            super(DefaultPriorConfig, self)
            .get(module_name, class_name, attribute_name)
            .replace(" ", "")
            .split(",")
        )
        return [arr[0]] + list(map(float, arr[1:]))


class LimitConfig(AncestorConfig):
    """Parses prior config"""

    def get(self, module_name, class_name, attribute_name):
        """

        Parameters
        ----------
        module_name: String
            The analysis_path of the module
        class_name: String
            The analysis_path of the class
        attribute_name: String
            The analysis_path of the attribute

        Returns
        -------
        prior_limits: ()
            A tuple containing the limits of the range of values an attribute can take
            with an exception being thrown if a nonlinear search produces a value
            outside of that range.
        """
        arr = (
            super(LimitConfig, self)
            .get(module_name, class_name, attribute_name)
            .replace(" ", "")
            .split(",")
        )
        return tuple(map(float, arr[:2]))
