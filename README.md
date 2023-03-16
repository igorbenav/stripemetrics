# stripemetrics 
___
> Compute metrics using stripe data and python 

> **Warning**
> This is still under development

## What is stripemetrics?

**stripemetrics** is a Python package that makes it easier for you to track metrics such as MRR, Churn and many more. 
It uses the stripe API to get the data, then computes your desired metrics.

## Features

  - Getting data from stripe API with **get_data()**
  - Monthly Recurring Revenue
  - Number of active users
  - Churn
  - Metrics by product
  
## Usage 

Importing stripemetrics:
```python
import stripemetrics
```

Getting Subscription data from stripe:
```python
get_data('Subscription', status='all', api_key='YOUR_STRIPE_KEY')
```
Pick one resource from Subscription, Product, Charge, etc

### Base Metrics:
- active_subscriptions
- active_subscribers
- new_subscribers
- new_subscriptions
- churn_dates
- subscription_churn_dates
- subscription_churn_dates
- churned_subscriptions

### Charge Metrics:
- total_revenue
- total_refunded
- total_refunds

### Subscription Metrics:
- total_mrr
- revenue_per_subscriber
- mrr_per_customer
- churned_subscribers_rate
- subscribers_retention_rate
- churned_subscriptions_rate
- subscription_retention_rate

> **Note**
> Some of the metrics mentioned need data enrichment (usually when using product filters), that is provided with the enrich_subscriptions and enrich_charges functions.

## Contributing

1. Fork it (https://github.com/igormagalhaesr/stripemetrics)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Dependencies

- [NumPy](https://www.numpy.org)
- [Pandas](https://pandas.pydata.org/)
- ...

## License

Distributed under the [BSD 3](LICENSE.txt) license. See ``LICENSE.txt`` for more information. 

## Contact

Igor Magalhaes – [@igormagalhaesr](https://twitter.com/igormagalhaesr) – igormagalhaesr@gmail.com

[github.com/igormagalhaesr](https://github.com/igormagalhaesr/)
