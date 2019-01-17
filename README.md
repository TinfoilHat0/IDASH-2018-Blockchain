# iDASH-2018-Blockchain-Track
Track 1: Blockchain-based immutable logging and querying for cross-site genomic dataset access audit trial

The goal of this track is to develop blockchain-based ledgering solutions to log and query the user activities of accessing genomic datasets (e.g., GTEx) across multiple sites.

## Experimental setting
Given a genomic data access log file, design a time/space efficient data structure and mechanisms to store and retrieve the logs based on MultiChain version 1.0.4 (https://www.multichain.com/download-install/).
Challenge: Each line in the data access log must be saved individually as one transaction (i.e., participants cannot save entire file in just one transaction), and all log data and intermediate data (such as index or cache) must be saved on-chain (no off-chain data storage allowed). It is up to you to determine how you choose to represent and store each line in transactions. It does not need to be a plain text copy of the log entry. Also, the query implementation should allow a user to search using any field of one log line (i.e., node, id, user, resource, activity, timestamp, and a “reference id” referring to the id of the original resource request), any “AND” combination (e.g., node AND id AND user AND resource), and any timestamp range (e.g., from 1522000002418 to 1522000011441) using a command-line interface. Also, the user should be able to sort the returning results in ascending/descending order with any field (e.g., timestamp). There will be 4 nodes in the blockchain network, and 4 log files to be stored. Users should be able to query the data from any of the 4 sites. Participants can implement any algorithm to store, retrieve and present the log data correctly and efficiently.

## Requirement
Submission requires open source code.

## Evaluation Criteria
The logging/querying system needs to demonstrate good performance (i.e., accurate query results) by using a testing dataset, which is different from the one provided online. We will evaluate the speed, storage/memory cost, and scalability of each solution. We will use the binary version of MultiChain 1.0.4 on 64-bit Ubuntu 14.04 with the default parameters as the test bed for fairness. No modification of the underlying MultiChain source code is allowed. The participants must consent to release any code or binaries submitted to the competition under the GNU General Public License v3.0 Open Source license. The submitted executable binaries should be non-interactive (i.e., depend only on parameters with no input required while it works), and should contain a readme file to specify the parameters. We will test all submissions using 4 virtual machines, each with 2-Core CPU, 8GB RAMs and 100GB storage.
