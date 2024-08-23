#include "utils.h"
#include <iostream>

void printStars(unsigned short timesStar, unsigned short starRows)
// prints starRows rows with timesStar stars
{
  for (unsigned short i = 0; i < starRows; i++)
  {
    std::cout << std::string(timesStar, '*') << '\n';
  }
}
void printVisible(const std::string& message)
// prints message within rows of stars to be easily found in large outputs
{
  printStars();
  std::cout << message << '\n';
  printStars();
}