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
    Console.WriteLine("Send or Recive test data (S or R or RB)? ");
    string sOR = Console.ReadLine().ToLower();
    while (sOR != "s" && sOR != "r" && sOR != "rb")
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
        case "rb":
            ReadPortBinary(serialPort);
            break;
    }
 }

void ReadPortBinary(SerialPort serialPort)
{
    serialPort.Open();
    serialPort.DataReceived += new SerialDataReceivedEventHandler(port_OnRecivedDataBinary);
    while (true) { }
}

void port_OnRecivedDataBinary(object sender, SerialDataReceivedEventArgs e)
{
    SerialPort serialPort = (SerialPort)sender;
    int bytesToRead = serialPort.BytesToRead;
    byte[] buffer = new byte[bytesToRead];
    serialPort.Read(buffer, 0, bytesToRead);

    Console.WriteLine("GOT DATA");
    foreach (byte b in buffer)
    {
        Console.WriteLine(b);
        //StringBuilder hex = new StringBuilder();
        //hex.AppendFormat("{0:x2}", b);
        //Console.WriteLine(hex.ToString());
    }
    Console.WriteLine();
}

void ReadPort(SerialPort serialPort)
{
    serialPort.Open();
    serialPort.DataReceived += new SerialDataReceivedEventHandler(port_OnRecivedData);
    while (true) { }
}

void port_OnRecivedData(object sender, SerialDataReceivedEventArgs e)
{
    SerialPort serialPort = (SerialPort)sender;
    int bytesToRead = serialPort.BytesToRead;
    if (bytesToRead >= 10)
    {
        byte[] buffer = new byte[bytesToRead];
        serialPort.Read(buffer, 0, bytesToRead);
        ProcessBytes(buffer);
    }
}


void ProcessBytes(byte[] bytes)
{
    for(int i = 0; i < bytes.Length; i++)
    {
        string message = "";
        if (bytes[i] == (byte)'C' && bytes[i + 1] == (byte)'R' && bytes[i + 2] == (byte)'E')
        {
            message += "CRE";
            message += (int)(bytes[i + 3]);
            for(int j = 0; j < 5; j++)
            {
                message += (char)(bytes[i + 4 + j]);
            }

            byte[] messageBytes = new byte[10];
            Array.Copy(bytes, i, messageBytes, 0, 9);
            byte checksum = ComputeAdditionChecksum(messageBytes);
            if(checksum == bytes[i+9])
            {
                Console.WriteLine(message);
            } else
            {
                Console.WriteLine("Message Failed Checksum");
            }
        }
    }
}

void WritePort(SerialPort serialPort)
{
    serialPort.Open();
    while (true)
    {
        Console.Write("Hit Enter to Send:");
        Console.ReadLine();
        Console.WriteLine("Sent");
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

        message[i] = ComputeAdditionChecksum(message);
        i++;

        serialPort.Write(message, 0, i + 1);
    }
}

byte ComputeAdditionChecksum(byte[] data)
{
    byte sum = 0;
    unchecked // Let overflow occur without exceptions
    {
        foreach (byte b in data)
        {
            sum += b;
        }
    }
    return sum;
}

Main();
