from django.test import TestCase

# Create your tests here.


with open('input.txt', 'r') as input_file:
    numbers = list(map(int, input_file.readline().split()))

result = sum(numbers)

with open('output.txt', 'w') as output_file:
    output_file.write(str(result) + '\n')
