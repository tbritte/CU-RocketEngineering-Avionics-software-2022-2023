using System;
using System.IO.Ports;

Console.WriteLine("Starting Antenna Tester!");
Console.WriteLine("Which COM Port Would You Like to Use? ");
string comPort = Console.ReadLine();

while(comPort == null)
{
    Console.WriteLine("Please enter a comm port:");
}

SerialPort serialPort = new SerialPort(portName: "COM1", baudRate: 57600, parity: Parity.None, dataBits: 8, stopBits: StopBits.One);

