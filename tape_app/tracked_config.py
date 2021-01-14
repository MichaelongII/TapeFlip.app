from tape_app.objects.pricing_option import PricingOption


class TrackedConfig:
    """
        Config class tracked by git.

        Keep config objects/vars that are used many times throughout the
        project.

        Is superclass to Config subclass that is untracked and that the site
        ultimetly gets it's config from.
    """

    PRICING_OPTIONS = [PricingOption(credits=10, price=10, desc_list=["Try it out"]),
                        PricingOption(credits=30, price=20, desc_list=["Good starting point"]),
                        PricingOption(credits=85, price=50, desc_list=["Great Value"]),
                        PricingOption(credits=200, price=100, desc_list=["Best Value"])]
