// Sample Code to Establish and Read OPC UA Data
using Opc.Ua;
using Opc.Ua.Client;
using Opc.Ua.Configuration;

var config = new ApplicationConfiguration()
{
    ApplicationName = "AWS OPC UA Client (ROG-G16)",
    ApplicationType = ApplicationType.Client,
    SecurityConfiguration = new SecurityConfiguration
    {
        ApplicationCertificate = new CertificateIdentifier()
        {
            StoreType = "Directory",
            StorePath = @"..\certificates\own\certs",
            SubjectName = "CN=AWS OPC UA Client (ROG-G16)"
        },
        TrustedPeerCertificates = new CertificateTrustList()
        {
            StoreType = "Directory",
            StorePath = @"..\certificates\trusted\certs"
        },
        RejectedCertificateStore = new CertificateTrustList()
        {
            StoreType = "Directory",
            StorePath = @"..\certificates\rejected\certs"
        },
        AutoAcceptUntrustedCertificates = true
    },
    TransportQuotas = new TransportQuotas { OperationTimeout = 15000 },
    ClientConfiguration = new ClientConfiguration { DefaultSessionTimeout = 60000 }
};

try
{
    // CHANGE: Replace with your OPC UA server's address and port
    var endpointUrl = "opc.tcp://192.168.1.100:4840";
    
    var endpoint = CoreClientUtils.SelectEndpoint(endpointUrl, true, 15000);
    
    // CHANGE: Replace with your actual username and password
    var userIdentity = new UserIdentity("admin", "password123");
    
    var session = await Session.Create(config, new ConfiguredEndpoint(null, endpoint),
        false, "AWS OPC UA Client Session", 60000, userIdentity, null);
    
    Console.WriteLine("Connected and authenticated successfully!");
    
    var browser = new Browser(session);
    var references = browser.Browse(ObjectIds.ObjectsFolder);
    
    foreach (var reference in references)
    {
        Console.WriteLine($"Node: {reference.DisplayName}");
        
        if (reference.NodeClass == NodeClass.Variable)
        {
            try
            {
                var value = session.ReadValue(reference.NodeId);
                Console.WriteLine($"  Value: {value.Value} (Type: {value.Value?.GetType().Name})");
                Console.WriteLine($"  Status: {value.StatusCode}");
                Console.WriteLine($"  Timestamp: {value.ServerTimestamp}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  Error reading value: {ex.Message}");
            }
        }
        Console.WriteLine();
    }
    
    session.Close();
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
}