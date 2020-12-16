"""
basic naive bayes classifier demonstration from scratch

Goal is to implement a naive bayes classifier from scratch using
only array and tabular data libraries like numpy and pandas.
Maybe some visualisation with matplotlib

The bayes formula:
    p(class|data) = p(data|class)p(class) / p(data)

Terms associated with this are:

- class: observable
- data: observable
- p(class|data): posterior distribution
- p(data|class): likelihood distribution
- p(class): prior distribution
- p(data): marginal distribution

Normally p(class) means number of observed value of class divided by all
the possible values of the class. For example, if we are talking about
weather class which can have 3 values: sunny, rainy, cloudy. p(sunny) = 1/3.
If our data contains sunny, sunny, rainy, cloudy. p(sunny) = 2/4 etc

In most cases likelihood distribution is based on gaussian. This means that
we apply the following formula for p(data|class):
(1 / sqrt(2* pi) * class_variance) *
exp((-(data-class_mean )**2) / (2*class_variance))

The data that needs to be associated with this model needs to be either in
tabular form where each observation is associated to some another with a value.
Or they need to come in a functional form where some distributions are modeled
as functions.

Remember that distributions help us to sample an existing material in different
ways that is all or model their generation.

This code depends heavily to this in its approach:
https://chrisalbon.com/machine_learning/naive_bayes/naive_bayes_classifier_from_scratch/

"""

import numpy as np
import pandas as pd

data = pd.DataFrame()

data["Coin"] = ["heads", "tails", "heads", "tails", "tails", "heads"]

data["Weight"] = [0.01, 0.01, 0.05, 0.01, 0.1, 0.1]
data["Length"] = [1, 1, 2, 2, 1.8, 1.7]
data["Width"] = [1, 1.01, 2.005, 2.1, 1.706, 1.708]

unknown_coin = pd.DataFrame()
unknown_coin["Weight"] = [0.03]
unknown_coin["Length"] = [1.4]
unknown_coin["Width"] = [1.6]

# in order to find unknown coin head or tail we need to find posteriors
# with presented evidence and prior, so p(heads|data) and p(tails|data)
# then we can select the maximum valued one to decide which one is more likely.


def px_given_y_gaussian(x, y_mean, y_stdev):
    "compute p(x|y) with gaussian distribution"
    term = 1 / (np.sqrt(2 * np.pi) * y_stdev)
    exponent = np.exp((-((x - y_mean) ** 2)) / (2 * (y_stdev * y_stdev)))
    return term * exponent


def px_prior(data: pd.DataFrame, x_category: str, observed_value):
    "count the number of occurence of an observed value under x category"
    value_counts = data[x_category].value_counts()
    # normalize values
    value_counts /= value_counts.sum()
    return value_counts.get(observed_value)


def compute_likelihood(
    data: pd.DataFrame,
    target_value,
    given_target_value,
    target_category,
    given_cat: str,
):
    "compute likelihood for target with given"
    target_group = data.loc[data[target_category] == target_value, :]
    given_mean_for_target = target_group[given_cat].mean()
    given_std_for_target = target_group[given_cat].std()
    return px_given_y_gaussian(
        given_target_value, given_mean_for_target, given_std_for_target
    )


def compute_likelihoods(
    data: pd.DataFrame, target_data, target_value, target_category: str
):
    "compute likelihood products for target category and value"
    cols = data.columns
    itercols = cols.drop([target_category])
    likelihood = 1.0
    for given_cat in itercols.array:
        given_target_val = target_data.get(given_cat).array[0]
        likelihood *= compute_likelihood(
            data, target_value, given_target_val, target_category, given_cat
        )
    return likelihood


def max_likelihood():
    "choose maximum likelihood"
    heads_prior = px_prior(data, "Coin", "heads")
    tails_prior = px_prior(data, "Coin", "tails")
    #
    heads_likelihood = compute_likelihoods(data, unknown_coin, "heads", "Coin")
    tails_likelihood = compute_likelihoods(data, unknown_coin, "tails", "Coin")
    p_heads_given_data = heads_prior * heads_likelihood
    p_tails_given_data = tails_prior * tails_likelihood
    if p_heads_given_data > p_tails_given_data:
        print("coin is most probably heads")
        print("p(heads|data): ", p_heads_given_data)
        print("p(tails|data): ", p_tails_given_data)
    else:
        print("coin is most probably tails")
        print("p(tails|data): ", p_tails_given_data)
        print("p(heads|data): ", p_heads_given_data)


if __name__ == "__main__":
    print("prior data:")
    print(data.head())
    print("given evidence:")
    print(unknown_coin.head())
    max_likelihood()
