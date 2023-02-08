using System;
using System.IO.Ports;
using System.Text;

void Main() {
    Console.WriteLine("Starting Antenna Tester!");

    // Output Available Ports
    Console.WriteLine("Comm Ports Available:\n");
    foreach (string portName in SerialPort.GetPortNames())
    {
        Console.Write(portName + ", ");
    }
    Console.Write("\n");

    // Get which port to use
    Console.WriteLine("Which COM Port Would You Like to Use? ");
    string comPort = Console.ReadLine();
    while (comPort == "" || comPort == null)
    {
        Console.WriteLine("Please enter a comm port:");
        comPort = Console.ReadLine();
    }

    // Get which port to use
    Console.WriteLine("Send or Recive test data (S or R)? ");
    string sOR = Console.ReadLine().ToLower();
    while (sOR != "s" && sOR != "r")
    {
        Console.WriteLine("Please enter a valid choice:");
        comPort = Console.ReadLine().ToLower();
    }

    SerialPort serialPort = new SerialPort(portName: comPort, baudRate: 57600, parity: Parity.None, dataBits: 8, stopBits: StopBits.One);

    switch(sOR)
    {
        case "s":
            WritePort(serialPort);
            break;
        case "r":
            ReadPort(serialPort);
            break;
    }
 }


void ReadPort(SerialPort serialPort)
{
    serialPort.Open();

    while (true)
    {
        int bytesToRead = serialPort.BytesToRead;
        byte[] buffer = new byte[bytesToRead];
        serialPort.Read(buffer, 0, bytesToRead);
    }
}

void ProcessBytes(byte[] bytes)
{
    
}

void WritePort(SerialPort serialPort)
{
    int i = 0;
    byte[] message = new byte[10];

    string header = "CRE";
    foreach (byte b in Encoding.ASCII.GetBytes(header))
    {
        message[i] = b;
        i++;
    }

    Random rnd = new Random();
    message[i] = (byte)rnd.Next(0, 256);
    i++;

    string chars = "Hello";
    Encoding.ASCII.GetBytes(chars);
    foreach (byte b in Encoding.ASCII.GetBytes(header))
    {
        message[i] = b;
        i++;
    }

    serialPort.Write(message, 0, i + 1);
}

