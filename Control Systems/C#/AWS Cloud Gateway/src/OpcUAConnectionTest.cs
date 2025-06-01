
// Sample Code to Establish and Read OPC UA Data

using Opc.Ua;
using Opc.Ua.Client;
using Opc.Ua.Configuration;

// Create application configuration
var config = new ApplicationConfiguration()
{
    ApplicationName = "AWS OPC UA Client (ROG-G16)",
    ApplicationType = ApplicationType.Client,
    SecurityConfiguration = new SecurityConfiguration
    {
        ApplicationCertificate = new CertificateIdentifier(),
        AutoAcceptUntrustedCertificates = true 
    },
    TransportConfigurations = new TransportConfigurationCollection(),
    TransportQuotas = new TransportQuotas { OperationTimeout = 15000 },
    ClientConfiguration = new ClientConfiguration { DefaultSessionTimeout = 60000 }
};

// Create session
var endpointUrl = "opc.tcp://your-server:4840";
var endpoint = CoreClientUtils.SelectEndpoint(endpointUrl, true, 15000);
var session = await Session.Create(config, new ConfiguredEndpoint(null, endpoint), 
    false, "OPC UA Client", 60000, new UserIdentity(), null);

// Browse the server
var browser = new Browser(session);
var references = browser.Browse(ObjectIds.ObjectsFolder);

foreach (var reference in references)
{
    Console.WriteLine($"Node: {reference.DisplayName}, NodeId: {reference.NodeId}");
}