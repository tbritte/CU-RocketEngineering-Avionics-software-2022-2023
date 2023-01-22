using System;
using System.IO.Ports;

Console.WriteLine("Hello, World!");

SerialPort serialPort = new SerialPort(portName: "COM1", baudRate: 57600, parity: Parity.None, dataBits: 8, stopBits: StopBits.One);

