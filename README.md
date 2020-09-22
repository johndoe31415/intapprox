# intapprox
Suppose you're on a 16-bit microcontroller. You measure a value with your ADC
and now you want to multiply it with 3. That's easy:

```
	uint16_t adc_value = read_adc();
	uint16_t result = adc_value * 3;
```

Now suppose you want to multiply by 2.5:

```
	uint16_t result = adc_value * 2.5;
```

This is going to get you into a world of pain if you're not used to
microcontroller programming, because typically you don't have an FPU. Hence the
floating point arithmetic needs to be emulated in software, which is
ridiculously, painfully slow. Instead, you'd rather do:

```
	uint16_t result = adc_value * 25 / 10;
```

Which is using only integer primitives. For the value 2.5, this is easy. But
suppose you want to multiply with Pi:

```
	uint16_t result = adc_value * 3141 / 1000;
```

This would work, if it were not for integer overflows. So this example works
for ADC values of 0 to 20, but things fly apart at ADC value 21 because 21 *
3141 = 65961, which is greater than the 16-bit CPU you're using.

The question is therefore: For a given set of constraints (e.g., input value
always in the range 0 to 511, CPU is 16 bit) and a given floating point value,
what is the ideal combination of multiplier and divisor that will give you the
most precise result?

## Usage
Luckily, this is exactly what this little tool does:

```
usage: intapprox.py [-h] [-b bits] -m int [-e epsilon] [--fast-multiplication]
                    [--fast-division] [-v]
                    expression

Approximate multiplication by a float value using integer arithmetic and
system constraints.

positional arguments:
  expression            Target expression to evaluate, which is the value that
                        the input is multiplied with. Must not include any
                        symbols.

optional arguments:
  -h, --help            show this help message and exit
  -b bits, --bits bits  Ensure that the topmost value never exceeds the
                        register width.
  -m int, --max-input-value int
                        Maximum input value that is expected.
  -e epsilon, --max-error epsilon
                        Error at which to abort. Defaults to 1.0e-06.
  --fast-multiplication
                        Only accept multiplication values that can be executed
                        quickly (i.e., by shifting left)
  --fast-division       Only accept divisor values that can be executed
                        quickly (i.e., by shifting right)
  -v, --verbose         Increases verbosity. Can be specified multiple times
                        to increase.
```

In our specific case, let's try it out:

```
$ ./intapprox.py -b 16 -m 511 3.141592653589793
Approximating target value: 3.141593
Best approximation        : x * 22 / 7
Resulting error           : 0.0402%
```

Now let's say we have a fast multiplier, but a slow dividing unit in our
hardware. Therefore, we would like to execute the division by using a binary
shift right. No problem:

```
$ ./intapprox.py -b 16 -m 511 --fast-div 3.141592653589793
Approximating target value: 3.141593
Best approximation        : x * 101 / 32
Resulting error           : 0.4666%
```

The error increases about tenfold, but it's still okay.

Now let's use a real world example that I had: 32-bit MCU, ADU values are 12
bit (0 to 4095). The voltage we're interested in is divided down heavily using
a 3.9k/12k voltage divider. We want to compute the original (source) voltage,
relative to the internal 1.2V reference voltage (STM32F103):

```
$ ./intapprox.py -v -b 32 -m 4095 '1.2 * 1000 / (3.9 / (3.9 + 12))'
Approximating target value: 4892.307692
Maximum input value       : 4095
Register width            : 32 bits
Maximum multiplier        : 1048832
Best approximation        : x * 63600 / 13
Resulting error           : 0.0000%
```

And we already have our answer.

## License
GNU GPL-3.
