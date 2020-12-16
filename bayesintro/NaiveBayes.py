"""
Main object that abstracts away concepts
introduced in BasicNaiveBayes.py
"""

import numpy as np
import pandas as pd
from typing import Set, List


from bayesutils import (
    Distribution,
    px_given_y_gaussian,
    px_given_y_gumbel,
    px_given_y_laplace,
    px_given_y_logistic,
)


class BasicNaiveBayesMLE:
    """!
    \brief Common methods for NaiveBayesMLE classes
    """

    def __init__(
        self,
        prior_data: pd.DataFrame,
        posterior_data: pd.Series,
        distribution_choice: Distribution = Distribution.GAUSSIAN,
    ):
        self.priors = prior_data
        self.posteriors = posterior_data
        self.distribution_fn = BasicNaiveBayesMLE.choose_distribution(
            distribution_choice
        )
        self.dist_choice = distribution_choice

    @staticmethod
    def choose_distribution(choice: Distribution):
        ""
        if choice == Distribution.GAUSSIAN:
            return px_given_y_gaussian
        elif choice == Distribution.LAPLACE:
            return px_given_y_laplace
        elif choice == Distribution.LOGISTIC:
            return px_given_y_logistic
        elif choice == Distribution.GUMBEL:
            return px_given_y_gumbel
        else:
            msg = "Distribution: " + choice
            msg += " is not implemented."
            raise NotImplementedError(msg)

    def prior_px(self, x_category: str, x_value):
        ""
        value_counts = self.priors[x_category].value_counts()
        # normalize values
        value_counts /= value_counts.sum()
        return value_counts.get(x_value)

    def compute_likelihood(
        self,
        target_observable_value,
        given_observable_value,
        target_observable_category: str,
        given_observable_category: str,
    ):
        ""
        target_group = self.priors.loc[
            self.priors[target_observable_category] == target_observable_value, :
        ]
        given_mean_for_target = target_group[given_observable_category].mean()
        given_std_for_target = target_group[given_observable_category].std()
        return self.distribution_fn(
            given_observable_value, given_mean_for_target, given_std_for_target
        )

    def compute_likelihoods(
        self, target_observable_value, target_observable_category: str
    ):
        ""
        cols = self.priors.columns
        itercols = cols.drop([target_observable_category])
        likelihood = 1.0
        for given_category in itercols.array:
            posterior_observable_value = self.posteriors.get(given_category)
            likelihood *= self.compute_likelihood(
                target_observable_value,
                posterior_observable_value,
                target_observable_category,
                given_category,
            )
        return likelihood

    def compute_max_likelihood(
        self, target_observable_category: str, target_observable_value
    ):
        ""
        target_prior = self.prior_px(
            x_category=target_observable_category, x_value=target_observable_value
        )
        target_likelihood = self.compute_likelihoods(
            target_observable_value, target_observable_category
        )
        return target_prior * target_likelihood

    def show_basic_info(self):
        ""
        print("Given prior data: ")
        print(self.priors.head())
        print("Given posterior data: ")
        print(self.posteriors.head())
        print("Given distrbution choice:", self.dist_choice)


class SingleNaiveBayesMLE(BasicNaiveBayesMLE):
    """!
    \brief Compute maximum likelihood for a posterior given as pd.Series

    We assume that there is only a single class/column whose value is unknown

    Small note: Since we are computing only maximum likelihood, we don't  we
    don't compute marginals which is common for all possible values.
    For more explanation, see:
    https://chrisalbon.com/machine_learning/naive_bayes/naive_bayes_classifier_from_scratch/

    Usage
    =====

    \code{.py}
    data = pd.DataFrame()

    data["Coin"] = ["heads", "tails", "heads", "tails", "tails", "heads"]

    data["Weight"] = [0.01, 0.01, 0.05, 0.01, 0.1, 0.1]
    data["Length"] = [1, 1, 2, 2, 1.8, 1.7]
    data["Width"] = [1, 1.01, 2.005, 2.1, 1.706, 1.708]

    unknown_coin = pd.DataFrame()
    unknown_coin["Weight"] = [0.03]
    unknown_coin["Length"] = [1.4]
    unknown_coin["Width"] = [1.6]

    classifier = SingleNaiveBayesMLE(
        prior_data=data, posterior_data=unknown_coin, target_category="Coin",
        distribution_choice=Distribution.GAUSSIAN
    )
    max_info = classifier.max_likelihood()
    single_classifier.show_result(max_info=max_info)

    
    \endcode

    This should output:

    ```
    Given prior data: 
        Coin  Weight  Length  Width
    0  heads    0.01     1.0  1.000
    1  tails    0.01     1.0  1.010
    2  heads    0.05     2.0  2.005
    3  tails    0.01     2.0  2.100
    4  tails    0.10     1.8  1.706
    Given posterior data: 
    Weight    0.03
    Length    1.40
    Width     1.60
    dtype: float64
    Given distrbution choice: Distribution.GAUSSIAN
    Posterior data has likely the following value:  heads
    For the category:  Coin
    With maximum likelihood value:  2.2013679914379907

    ```
    """

    def __init__(
        self,
        prior_data: pd.DataFrame,
        posterior_data: pd.Series,
        distribution_choice: Distribution = Distribution.GAUSSIAN,
        target_category: str = None,
    ):
        super().__init__(
            prior_data=prior_data,
            posterior_data=posterior_data,
            distribution_choice=distribution_choice,
        )
        self.target_category = target_category

    def max_likelihood(self, target_category=None):
        ""
        target_cat = None
        if target_category is None and self.target_category is None:
            msg = "You should either provide a target value"
            msg += " as argument of this function or pass a value "
            msg += "during instantiation of this class"
            raise ValueError(msg)
        elif target_category is not None:
            target_cat = target_category
        else:
            target_cat = self.target_category

        target_values = self.priors[target_cat].array
        max_target_observable_value = None
        max_value = float("-inf")
        for target_observable_value in target_values:
            maxval = self.compute_max_likelihood(target_cat, target_observable_value)
            if maxval > max_value:
                max_value = maxval
                max_target_observable_value = target_observable_value
        return {
            "target-observable-value": max_target_observable_value,
            "maximum-likelihood-value": max_value,
            "target-observable-class": target_cat,
        }

    def show_result(self, target_category=None, max_info=None):
        ""
        if max_info is None:
            max_info = self.max_likelihood(target_category)
        self.show_basic_info()
        print(
            "Posterior data has likely the following value: ",
            max_info["target-observable-value"],
        )
        print("For the category: ", max_info["target-observable-class"])
        print("With maximum likelihood value: ", max_info["maximum-likelihood-value"])


class MultiNaiveBayesMLE(BasicNaiveBayesMLE):
    """!
    \brief Compute maximum likelihood for a posterior given as pd.Series

    We assume that we have several class/columns whose values are unknown

    \see SingleNaiveBayesMLE for MLE note

    Our approach is simple:
    We compute the MLE values for each possible value of unknown classes.
    We choose the maximum, plug it into posterior data and recompute MLE's
    for remaining unknowns until each field of series is filled
    """

    def __init__(
        self,
        prior_data: pd.DataFrame,
        posterior_data: pd.Series,
        target_categories: Set[str],
        distribution_choice: Distribution = Distribution.GAUSSIAN,
    ):
        super().__init__(
            prior_data=prior_data,
            posterior_data=posterior_data,
            distribution_choice=distribution_choice,
        )
        self.target_categories = target_categories
        self.added_categories: Set[str] = set()
        self.added_max_infos: List[dict] = []

    def single_max_likelihood(self, target_category: str):
        ""
        single_mle = SingleNaiveBayesMLE(
            prior_data=self.priors.copy(),
            posterior_data=self.posteriors.copy(),
            distribution_choice=self.dist_choice,
        )
        max_info = single_mle.max_likelihood(target_category)
        return max_info

    def is_addable(self) -> bool:
        return len(self.target_categories - self.added_categories) > 0

    def set_prior_max_likelihood(self):
        ""
        current_categories = self.target_categories - self.added_categories
        max_likelihood = float("-inf")
        minfo = None
        for current_category in current_categories:
            max_info = self.single_max_likelihood(current_category)
            if max_info["maximum-likelihood-value"] > max_likelihood:
                minfo = max_info
                max_likelihood = max_info["maximum-likelihood-value"]
        #
        # set values to posteriors
        self.posteriors[minfo["target-observable-class"]] = minfo[
            "target-observable-value"
        ]
        self.added_categories.add(minfo["target-observable-class"])
        self.added_max_infos.append(minfo)

    def max_likelihood(self):
        ""
        while self.is_addable():
            self.set_prior_max_likelihood()

    def show_result(self):
        ""
        if len(self.added_max_infos) == 0:
            self.max_likelihood()
        self.show_basic_info()
        print(
            "The following information can be shown with respect to",
            "filling the posterior",
        )
        for index, max_info in enumerate(self.added_max_infos):
            print("Following information is added to posterior at", index, "iteration")
            print("It had: ")
            print("the value: ", max_info["target-observable-value"])
            print("For the category: ", max_info["target-observable-class"])
            print(
                "With maximum likelihood value: ", max_info["maximum-likelihood-value"],
            )


if __name__ == "__main__":
    # simple test
    data = pd.DataFrame()

    data["Coin"] = ["heads", "tails", "heads", "tails", "tails", "heads"]

    data["Weight"] = [0.01, 0.01, 0.05, 0.01, 0.1, 0.1]
    data["Length"] = [1, 1, 2, 2, 1.8, 1.7]
    data["Width"] = [1, 1.01, 2.005, 2.1, 1.706, 1.708]

    unknown_coin = pd.Series(dtype=np.float64)
    unknown_coin["Weight"] = 0.03
    unknown_coin["Length"] = 1.4
    unknown_coin["Width"] = 1.6
    #
    unknown_coin2 = pd.Series(dtype=np.float64)
    unknown_coin2["Weight"] = 0.07

    single_classifier = SingleNaiveBayesMLE(
        prior_data=data.copy(),
        posterior_data=unknown_coin.copy(),
        target_category="Coin",
        distribution_choice=Distribution.GAUSSIAN,
    )
    max_info = single_classifier.max_likelihood()
    single_classifier.show_result(max_info=max_info)

    # multi try
    multi_classifier = MultiNaiveBayesMLE(
        prior_data=data.copy(),
        posterior_data=unknown_coin2.copy(),
        target_categories=set(["Coin", "Length", "Width"]),
        distribution_choice=Distribution.GAUSSIAN,
    )
    multi_classifier.show_result()
