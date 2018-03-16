-module(protocol_util).

-export([encode_string/2, decode_string/1, encode_list/2, decode_list/2]).

-include("protocol.hrl").

encode_string(S, BuffLen) ->
	DataLen = length(S),
	Bin = list_to_binary(S),
	if 
		DataLen == BuffLen ->
			<<BuffLen:?UINT16, Bin/binary>>;
		DataLen > BuffLen ->			
			<<BuffLen:?UINT16, (element(1, split_binary(Bin, BuffLen)))/binary>>;
		DataLen < BuffLen ->
			<<BuffLen:?UINT16, Bin/binary, 0:((BuffLen-DataLen)*8)>> 
	end.
decode_string(Bin) ->
	<<DataLen:?UINT16, Bin1>> = Bin,
	split_binary(DataLen, Bin1).

encode_list(EncodeFun, L) ->
	Bin = <<(length(L)):?UINT16>>,
	encode_list(EncodeFun, L, Bin).
encode_list(_EncodeFun, [], Bin) ->
	Bin;
encode_list(EncodeFun, [H | T], Bin) ->	
	encode_list(EncodeFun, T, <<Bin/binary, (EncodeFun(H))/binary>>).

decode_list(DecodeFun, BinData) ->
	<<Count:?UINT16, BinData1/binary>> = BinData,
	decode_list(DecodeFun, BinData1, Count, []).
decode_list(_DecodeFun, BinData, 0, Result) ->
	{Result, BinData};
decode_list(DecodeFun, BinData, Count, Result) ->
	{E, BinData1} = DecodeFun(BinData),
	decode_list(DecodeFun, BinData1, Count-1, [E | Result]).

 
	

	
