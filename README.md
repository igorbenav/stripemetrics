# stripemetrics
___
>Compute metrics using stripe data and python

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
get_data(Subscription, api_key='YOUR_STRIPE_KEY')
```

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
